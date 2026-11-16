from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from flask import Flask
from flask.testing import FlaskClient

from participium.core.exceptions import ValidationError
from participium.models.enums import ReportStatus, Role
from participium.routes import api


@pytest.fixture
def app() -> Flask:
    application = Flask(__name__)
    return application


@pytest.fixture
def controller_bundle() -> SimpleNamespace:
    return SimpleNamespace(
        auth=Mock(),
        users=Mock(),
        reports=Mock(),
        operators=Mock(),
        admin=Mock(),
        statistics=Mock(),
        repositories={},
    )


def test_as_bool_converts_values_correctly() -> None:
    assert api._as_bool(None, default=True) is True
    assert api._as_bool(True) is True
    assert api._as_bool(False) is False
    assert api._as_bool("true") is True
    assert api._as_bool("Yes") is True
    assert api._as_bool("1") is True
    assert api._as_bool("off") is False
    assert api._as_bool("0") is False
    assert api._as_bool("no") is False


def test_parse_report_status_returns_enum_and_raises_for_invalid() -> None:
    assert api._parse_report_status("Assigned") is ReportStatus.ASSIGNED
    assert api._parse_report_status(None) is None

    with pytest.raises(ValidationError, match="Invalid report status filter"):
        api._parse_report_status("not-a-status")


def test_register_user_api_exposes_verification_url_when_enabled(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    user = SimpleNamespace(id=1, username="citizen")
    controller_bundle.auth.register.return_value = (user, "http://localhost/api/v1/auth/verify/abc")
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr(api, "serialize_user", Mock(return_value={"id": 1, "username": "citizen"}))
    app.config["SETTINGS"] = SimpleNamespace(expose_verification_links=True)

    with app.test_request_context(
        "/api/v1/auth/register",
        method="POST",
        json={"username": "citizen", "email": "citizen@example.com", "password": "pass"},
    ):
        response, status_code = api.register_user_api()

    assert status_code == 201
    assert response.get_json() == {
        "user": {"id": 1, "username": "citizen"},
        "verification_url": "http://localhost/api/v1/auth/verify/abc",
    }


def test_register_user_api_hides_verification_url_when_disabled(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    user = SimpleNamespace(id=1, username="citizen")
    controller_bundle.auth.register.return_value = (user, "http://localhost/api/v1/auth/verify/abc")
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr(api, "serialize_user", Mock(return_value={"id": 1, "username": "citizen"}))
    app.config["SETTINGS"] = SimpleNamespace(expose_verification_links=False)

    with app.test_request_context(
        "/api/v1/auth/register",
        method="POST",
        json={"username": "citizen", "email": "citizen@example.com", "password": "pass"},
    ):
        response, status_code = api.register_user_api()

    assert status_code == 201
    assert response.get_json() == {"user": {"id": 1, "username": "citizen"}}


def test_report_filters_parses_query_parameters(app: Flask) -> None:
    with app.test_request_context(
        "/api/v1/reports?category_id=5&status=Assigned&date_from=2024-01-01T00:00:00&date_to=2024-01-31T23:59:59&sort=asc"
    ):
        filters = api._report_filters()

    assert filters["category_id"] == 5
    assert filters["status"] is ReportStatus.ASSIGNED
    assert filters["sort"] == "asc"
    assert isinstance(filters["date_from"], datetime)
    assert isinstance(filters["date_to"], datetime)


def test_update_admin_user_api_converts_boolean_fields(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    controller_bundle.admin.update_user.return_value = {"id": 8, "username": "bob"}
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=SimpleNamespace(id=1, role=Role.ADMIN)))
    monkeypatch.setattr(api, "serialize_user", Mock(return_value={"id": 8, "username": "bob"}))

    with app.test_request_context(
        "/api/v1/admin/users/8",
        method="PUT",
        json={"is_active": "true", "email_notifications_enabled": "on", "role": "operator"},
    ):
        response = api.update_admin_user_api(8)

    assert response.get_json() == {"id": 8, "username": "bob"}
    controller_bundle.admin.update_user.assert_called_once()
    args, kwargs = controller_bundle.admin.update_user.call_args
    assert args[0] == 8
    assert args[1]["is_active"] is True
    assert args[1]["email_notifications_enabled"] is True
    assert args[1]["role"] == "operator"


def test_update_admin_user_api_skips_missing_boolean_fields(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    controller_bundle.admin.update_user.return_value = {"id": 8, "username": "bob"}
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=SimpleNamespace(id=1, role=Role.ADMIN)))
    monkeypatch.setattr(api, "serialize_user", Mock(return_value={"id": 8, "username": "bob"}))

    with app.test_request_context(
        "/api/v1/admin/users/8",
        method="PUT",
        json={"role": "operator"},
    ):
        response = api.update_admin_user_api(8)

    assert response.get_json() == {"id": 8, "username": "bob"}
    args, kwargs = controller_bundle.admin.update_user.call_args
    assert args[0] == 8
    assert args[1] == {"role": "operator"}


def test_update_category_api_parses_is_active_flag(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    controller_bundle.admin.update_category.return_value = {"id": 3, "name": "Strade", "is_active": False}
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=SimpleNamespace(id=1, role=Role.ADMIN)))
    monkeypatch.setattr(api, "serialize_category", Mock(return_value={"id": 3, "name": "Strade", "is_active": False}))

    with app.test_request_context(
        "/api/v1/admin/categories/3",
        method="PUT",
        json={"is_active": "false"},
    ):
        response = api.update_category_api(3)

    assert response.get_json() == {"id": 3, "name": "Strade", "is_active": False}
    controller_bundle.admin.update_category.assert_called_once()
    _, payload = controller_bundle.admin.update_category.call_args[0]
    assert payload["is_active"] is False


def test_update_category_api_without_is_active_field_uses_payload_as_is(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    controller_bundle.admin.update_category.return_value = SimpleNamespace(id=3, name="Strade")
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=SimpleNamespace(id=1, role=Role.ADMIN)))
    monkeypatch.setattr(api, "serialize_category", Mock(return_value={"id": 3, "name": "Strade"}))

    with app.test_request_context(
        "/api/v1/admin/categories/3",
        method="PUT",
        json={"name": "Strade"},
    ):
        response = api.update_category_api(3)

    assert response.get_json() == {"id": 3, "name": "Strade"}
    args, kwargs = controller_bundle.admin.update_category.call_args
    assert args[0] == 3
    assert args[1] == {"name": "Strade"}


def test_export_reports_api_returns_csv(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    controller_bundle.reports.export_rows.return_value = [
        {"id": 1, "title": "Pothole", "category": "Road", "status": "Published", "created_at": "2024-01-01", "latitude": 45.0, "longitude": 7.0}
    ]
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))

    with app.test_request_context(
        "/api/v1/reports/export?status=Assigned&category_id=1&sort=desc",
        method="GET",
    ):
        response = api.export_reports_api()

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment; filename=participium_reports.csv" in response.headers["Content-Disposition"]
    assert "id,title,category,status,created_at,latitude,longitude" in response.get_data(as_text=True)
    assert "Pothole" in response.get_data(as_text=True)


def test_update_me_api_converts_email_notifications_from_form(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    controller_bundle.users.update_profile.return_value = {"id": 2, "username": "alice"}
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=SimpleNamespace(id=2)))
    monkeypatch.setattr(api, "current_user", Mock(return_value=SimpleNamespace(id=2)))
    monkeypatch.setattr(api, "serialize_user", Mock(return_value={"id": 2, "username": "alice"}))

    with app.test_request_context(
        "/api/v1/users/me",
        method="PUT",
        data={"username": "alice", "email_notifications_enabled": "on"},
    ):
        response = api.update_me_api()

    assert response.get_json() == {"id": 2, "username": "alice"}
    controller_bundle.users.update_profile.assert_called_once()
    _, kwargs = controller_bundle.users.update_profile.call_args
    assert kwargs["username"] == "alice"
    assert kwargs["email_notifications_enabled"] is True


def test_update_me_api_converts_email_notifications_from_json(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    controller_bundle.users.update_profile.return_value = {"id": 2, "username": "alice"}
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=SimpleNamespace(id=2)))
    monkeypatch.setattr(api, "current_user", Mock(return_value=SimpleNamespace(id=2)))
    monkeypatch.setattr(api, "serialize_user", Mock(return_value={"id": 2, "username": "alice"}))

    with app.test_request_context(
        "/api/v1/users/me",
        method="PUT",
        json={"username": "alice", "email_notifications_enabled": "true"},
    ):
        response = api.update_me_api()

    assert response.get_json() == {"id": 2, "username": "alice"}
    controller_bundle.users.update_profile.assert_called_once()
    _, kwargs = controller_bundle.users.update_profile.call_args
    assert kwargs["username"] == "alice"
    assert kwargs["email_notifications_enabled"] is True


def test_update_me_api_ignores_missing_email_notifications_flag(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    controller_bundle.users.update_profile.return_value = {"id": 2, "username": "alice"}
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=SimpleNamespace(id=2)))
    monkeypatch.setattr(api, "current_user", Mock(return_value=SimpleNamespace(id=2)))
    monkeypatch.setattr(api, "serialize_user", Mock(return_value={"id": 2, "username": "alice"}))

    with app.test_request_context(
        "/api/v1/users/me",
        method="PUT",
        json={"username": "alice"},
    ):
        response = api.update_me_api()

    assert response.get_json() == {"id": 2, "username": "alice"}
    controller_bundle.users.update_profile.assert_called_once()
    _, kwargs = controller_bundle.users.update_profile.call_args
    assert kwargs["username"] == "alice"
    assert kwargs["email_notifications_enabled"] is None


def test_mark_notification_read_api_uses_current_user_and_serializes_result(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    notification = object()
    controller_bundle.users.get_notification_for_user.return_value = notification
    controller_bundle.users.mark_notification_as_read.return_value = notification
    mock_serialized = {"id": 11, "read": True}
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(api, "current_user", Mock(return_value=SimpleNamespace(id=7)))
    monkeypatch.setattr(api, "serialize_notification", Mock(return_value=mock_serialized))

    with app.test_request_context(
        "/api/v1/users/me/notifications/11/read",
        method="POST",
    ):
        response = api.mark_notification_read_api(11)

    assert response.get_json() == mock_serialized
    controller_bundle.users.get_notification_for_user.assert_called_once_with(7, 11)
    controller_bundle.users.mark_notification_as_read.assert_called_once_with(notification)


def test_payload_returns_form_data_when_json_missing(app: Flask) -> None:
    with app.test_request_context(
        "/api/v1/dummy",
        method="POST",
        data={"name": "test", "is_active": "true"},
    ):
        payload = api._payload()

    assert payload["name"] == "test"
    assert payload["is_active"] == "true"


def test_send_message_api_routes_to_controller_and_serializes(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    controller_bundle.reports.build_detail_context.return_value = SimpleNamespace(report=SimpleNamespace(id=1), can_access_messages=True)
    controller_bundle.reports.send_message.return_value = SimpleNamespace(id=5, body="Hello")
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=SimpleNamespace(id=4, role=Role.CITIZEN)))
    monkeypatch.setattr(api, "current_user", Mock(return_value=SimpleNamespace(id=4, role=Role.CITIZEN)))
    monkeypatch.setattr(api, "serialize_message", Mock(return_value={"id": 5, "body": "Hello"}))

    with app.test_request_context(
        "/api/v1/reports/1/messages",
        method="POST",
        json={"body": "Hello"},
    ):
        response, status_code = api.send_message_api(1)

    assert status_code == 201
    assert response.get_json() == {"id": 5, "body": "Hello"}
    controller_bundle.reports.send_message.assert_called_once()


def test_public_stats_api_returns_statistics(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {"count": 7}
    controller_bundle.statistics.public_statistics.return_value = expected
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))

    with app.test_request_context(
        "/api/v1/stats/public?granularity=week",
        method="GET",
    ):
        response = api.public_stats_api()

    assert response.get_json() == expected
    controller_bundle.statistics.public_statistics.assert_called_once_with("week")


def test_me_api_returns_current_user_profile(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    current = SimpleNamespace(id=2, username="alice")
    monkeypatch.setattr(api, "current_user", Mock(return_value=current))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=current))
    monkeypatch.setattr(api, "serialize_user", Mock(return_value={"id": 2, "username": "alice"}))

    with app.test_request_context(
        "/api/v1/users/me",
        method="GET",
    ):
        response = api.me_api()

    assert response.get_json() == {"id": 2, "username": "alice"}


def test_delete_me_api_calls_delete_and_logout(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    current = SimpleNamespace(id=3, username="bob")
    controller_bundle.users.delete_account.return_value = None
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr(api, "current_user", Mock(return_value=current))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=current))
    monkeypatch.setattr(api, "logout_user", Mock())

    with app.test_request_context(
        "/api/v1/users/me",
        method="DELETE",
    ):
        response = api.delete_me_api()

    assert response.get_json() == {"message": "Account deleted."}
    controller_bundle.users.delete_account.assert_called_once_with(current)
    api.logout_user.assert_called_once()


def test_my_reports_api_lists_owned_reports(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    current = SimpleNamespace(id=10, username="carla")
    report = SimpleNamespace(id=1)
    controller_bundle.reports.list_user_reports.return_value = [report]
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr(api, "current_user", Mock(return_value=current))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=current))
    monkeypatch.setattr(api, "serialize_report_summary", Mock(return_value={"id": 1}))

    with app.test_request_context(
        "/api/v1/users/me/reports",
        method="GET",
    ):
        response = api.my_reports_api()

    assert response.get_json() == [{"id": 1}]
    controller_bundle.reports.list_user_reports.assert_called_once_with(current)


def test_my_notifications_api_returns_serialized_notifications(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    current = SimpleNamespace(id=20)
    controller_bundle.users.list_notifications.return_value = [SimpleNamespace(id=33)]
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr(api, "current_user", Mock(return_value=current))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=current))
    monkeypatch.setattr(api, "serialize_notification", Mock(return_value={"id": 33}))

    with app.test_request_context(
        "/api/v1/users/me/notifications",
        method="GET",
    ):
        response = api.my_notifications_api()

    assert response.get_json() == [{"id": 33}]
    controller_bundle.users.list_notifications.assert_called_once_with(20)


def test_pending_and_assigned_reports_api_use_dashboard_context(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    current = SimpleNamespace(id=12, role=Role.OPERATOR)
    dashboard_context = SimpleNamespace(
        pending_reports=[SimpleNamespace(id=1)],
        assigned_reports=[SimpleNamespace(id=2)],
        unread_message_counts={2: 5},
    )
    controller_bundle.operators.build_dashboard.return_value = dashboard_context
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr(api, "current_user", Mock(return_value=current))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=current))
    monkeypatch.setattr(api, "serialize_report_summary", Mock(side_effect=[{"id": 1}, {"id": 2}]))

    with app.test_request_context(
        "/api/v1/operator/reports/pending",
        method="GET",
    ):
        response_pending = api.pending_reports_api()

    with app.test_request_context(
        "/api/v1/operator/reports/assigned",
        method="GET",
    ):
        response_assigned = api.assigned_reports_api()

    assert response_pending.get_json() == [{"id": 1}]
    assert response_assigned.get_json() == [{"id": 2, "unread_message_count": 5}]
    controller_bundle.operators.build_dashboard.assert_called()


def test_assign_report_api_calls_operator_assign(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    current = SimpleNamespace(id=14, role=Role.OPERATOR)
    controller_bundle.operators.assign_report.return_value = SimpleNamespace(id=7)
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr(api, "current_user", Mock(return_value=current))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=current))
    monkeypatch.setattr(api, "serialize_report_detail", Mock(return_value={"id": 7}))

    with app.test_request_context(
        "/api/v1/operator/reports/7/assign",
        method="POST",
    ):
        response = api.assign_report_api(7)

    assert response.get_json() == {"id": 7}
    controller_bundle.operators.assign_report.assert_called_once_with(7, current)


def test_update_report_status_api_calls_operator_update_status(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    current = SimpleNamespace(id=15, role=Role.OPERATOR)
    controller_bundle.operators.update_status.return_value = SimpleNamespace(id=8)
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr(api, "current_user", Mock(return_value=current))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=current))
    monkeypatch.setattr(api, "serialize_report_detail", Mock(return_value={"id": 8}))

    with app.test_request_context(
        "/api/v1/operator/reports/8/status",
        method="POST",
        json={"status": "Resolved", "note": "Done"},
    ):
        response = api.update_report_status_api(8)

    assert response.get_json() == {"id": 8}
    controller_bundle.operators.update_status.assert_called_once_with(8, current, "Resolved", "Done")


def test_admin_users_and_categories_endpoints_work(app: Flask, controller_bundle: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    current = SimpleNamespace(id=16, role=Role.ADMIN)
    controller_bundle.admin.list_users.return_value = [SimpleNamespace(id=9)]
    controller_bundle.admin.create_user.return_value = SimpleNamespace(id=10)
    controller_bundle.admin.list_categories.return_value = [SimpleNamespace(id=11)]
    controller_bundle.admin.admin_statistics.return_value = {"users": 1}
    controller_bundle.admin.create_category.return_value = SimpleNamespace(id=12)
    monkeypatch.setattr(api, "get_controllers", Mock(return_value=controller_bundle))
    monkeypatch.setattr(api, "current_user", Mock(return_value=current))
    monkeypatch.setattr("participium.core.auth.current_user", Mock(return_value=current))
    monkeypatch.setattr(api, "serialize_user", Mock(side_effect=[{"id": 9}, {"id": 10}]))
    monkeypatch.setattr(api, "serialize_category", Mock(return_value={"id": 11}))

    with app.test_request_context(
        "/api/v1/admin/users",
        method="GET",
    ):
        response_users = api.admin_users_api()

    with app.test_request_context(
        "/api/v1/admin/users",
        method="POST",
        json={"username": "admin", "role": "admin"},
    ):
        response_create_user, status_code_create = api.create_admin_user_api()

    with app.test_request_context(
        "/api/v1/admin/categories",
        method="GET",
    ):
        response_categories = api.admin_categories_api()

    with app.test_request_context(
        "/api/v1/admin/categories",
        method="POST",
        json={"name": "New"},
    ):
        response_create_category, status_code_category = api.create_category_api()

    with app.test_request_context(
        "/api/v1/admin/stats",
        method="GET",
    ):
        response_stats = api.admin_stats_api()

    assert response_users.get_json() == [{"id": 9}]
    assert status_code_create == 201
    assert response_create_user.get_json() == {"id": 10}
    assert response_categories.get_json() == [{"id": 11}]
    assert status_code_category == 201
    assert response_create_category.get_json() == {"id": 11}
    assert response_stats.get_json() == {"users": 1}
