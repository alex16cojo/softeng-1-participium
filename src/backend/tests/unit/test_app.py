from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from flask import g, jsonify
from flask.testing import FlaskClient

from participium.app import create_app
from participium.config.settings import Settings
from participium.core.exceptions import DomainError


def make_settings(**overrides) -> Settings:
    settings = Settings(
        app_name="Participium",
        secret_key="secret",
        debug=True,
        frontend_origin="http://localhost:5173",
        host="127.0.0.1",
        port=5050,
        auto_init_db=False,
        bootstrap_reference_data=False,
        bootstrap_demo_data=False,
        mail_backend="console",
        mail_from="noreply@example.com",
        mail_outbox_dir=(Path.cwd() / "build" / "outbox").resolve(),
        smtp_host=None,
        smtp_port=587,
        smtp_username=None,
        smtp_password=None,
        smtp_use_tls=True,
        expose_verification_links=True,
        media_root=(Path.cwd() / "build" / "media").resolve(),
        max_content_length=16 * 1024 * 1024,
        instance_path=(Path.cwd() / "build" / "instance").resolve(),
    )
    for key, value in overrides.items():
        setattr(settings, key, value)
    return settings


def patch_startup_dependencies(monkeypatch):
    mock_open_connection = Mock()
    mock_app_container = Mock(return_value=object())
    mock_init_swagger = Mock()
    mock_register_blueprints = Mock()
    mock_create_all = Mock()
    mock_seed_reference_data = Mock()
    mock_seed_demo_data = Mock()
    mock_get_session = Mock(return_value="session")
    mock_remove_session = Mock()

    monkeypatch.setattr("participium.app.open_connection", mock_open_connection)
    monkeypatch.setattr("participium.app.AppContainer", mock_app_container)
    monkeypatch.setattr("participium.app.init_swagger", mock_init_swagger)
    monkeypatch.setattr("participium.app.register_blueprints", mock_register_blueprints)
    monkeypatch.setattr("participium.app.create_all", mock_create_all)
    monkeypatch.setattr("participium.app.seed_reference_data", mock_seed_reference_data)
    monkeypatch.setattr("participium.app.seed_demo_data", mock_seed_demo_data)
    monkeypatch.setattr("participium.app.get_session", mock_get_session)
    monkeypatch.setattr("participium.app.remove_session", mock_remove_session)

    return {
        "open_connection": mock_open_connection,
        "AppContainer": mock_app_container,
        "init_swagger": mock_init_swagger,
        "register_blueprints": mock_register_blueprints,
        "create_all": mock_create_all,
        "seed_reference_data": mock_seed_reference_data,
        "seed_demo_data": mock_seed_demo_data,
        "get_session": mock_get_session,
        "remove_session": mock_remove_session,
    }


def test_create_app_does_not_seed_database_when_auto_init_db_is_disabled(monkeypatch):
    patches = patch_startup_dependencies(monkeypatch)

    settings = make_settings(auto_init_db=False)
    app = create_app(settings)

    patches["open_connection"].assert_called_once()
    patches["AppContainer"].assert_called_once_with(settings)
    patches["create_all"].assert_not_called()
    patches["seed_reference_data"].assert_not_called()
    patches["seed_demo_data"].assert_not_called()
    assert app.config["SECRET_KEY"] == "secret"
    assert app.config["MAX_CONTENT_LENGTH"] == 16 * 1024 * 1024
    assert app.extensions["container"] is patches["AppContainer"].return_value


def test_create_app_initializes_and_seeds_database_when_flags_are_enabled(monkeypatch):
    patches = patch_startup_dependencies(monkeypatch)

    settings = make_settings(
        auto_init_db=True,
        bootstrap_reference_data=True,
        bootstrap_demo_data=True,
    )
    create_app(settings)

    patches["create_all"].assert_called_once()
    assert patches["get_session"].call_count == 2
    patches["seed_reference_data"].assert_called_once_with("session")
    patches["seed_demo_data"].assert_called_once_with("session", settings.media_root)


def test_before_request_loads_active_user_into_g(monkeypatch):
    patches = patch_startup_dependencies(monkeypatch)

    settings = make_settings()
    user = SimpleNamespace(is_active=True, username="alice")
    repository = Mock()
    repository.get_by_id.return_value = user
    monkeypatch.setattr("participium.app.UserRepository", Mock(return_value=repository))

    app = create_app(settings)

    @app.route("/test-current-user")
    def test_current_user():
        return jsonify({"username": g.current_user.username if g.current_user else None})

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 7

        response = client.get("/test-current-user")

        assert response.status_code == 200
        assert response.get_json() == {"username": "alice"}

        with client.session_transaction() as sess:
            assert sess["user_id"] == 7


def test_before_request_removes_inactive_user_from_session(monkeypatch):
    patches = patch_startup_dependencies(monkeypatch)

    settings = make_settings()
    user = SimpleNamespace(is_active=False)
    repository = Mock()
    repository.get_by_id.return_value = user
    monkeypatch.setattr("participium.app.UserRepository", Mock(return_value=repository))

    app = create_app(settings)

    @app.route("/test-current-user")
    def test_current_user():
        return jsonify({"username": g.current_user.username if g.current_user else None})

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 14

        response = client.get("/test-current-user")

        assert response.status_code == 200
        assert response.get_json() == {"username": None}

        with client.session_transaction() as sess:
            assert "user_id" not in sess


def test_teardown_appcontext_removes_database_session(monkeypatch):
    patches = patch_startup_dependencies(monkeypatch)

    settings = make_settings()
    app = create_app(settings)

    with app.app_context():
        pass

    patches["remove_session"].assert_called_once()


def test_domain_error_handler_returns_json_status_and_message(monkeypatch):
    patch_startup_dependencies(monkeypatch)

    settings = make_settings()
    app = create_app(settings)

    @app.route("/boom")
    def boom():
        raise DomainError("oops", status_code=418)

    client = app.test_client()
    response = client.get("/boom")

    assert response.status_code == 418
    assert response.get_json() == {"error": "oops"}


def test_404_error_handler_returns_standard_json_response(monkeypatch):
    patch_startup_dependencies(monkeypatch)

    settings = make_settings()
    app = create_app(settings)

    client = app.test_client()
    response = client.get("/missing-route")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Resource not found."}
