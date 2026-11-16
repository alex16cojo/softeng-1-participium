from __future__ import annotations

import io
from http.client import responses
from unittest.mock import Mock

import pytest

from pytest import MonkeyPatch
from flask.testing import FlaskClient

from participium.app import create_app
from participium.database import close_connection, get_session
from participium.models import Category, EmailVerificationToken, Report, Message
from participium.models.enums import ReportStatus
from participium.models.user import User
from datetime import datetime, timedelta
from participium.models.enums import Role

@pytest.fixture
def bootstrap_app(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    
    monkeypatch.setenv("AUTO_INIT_DB", "true")
    monkeypatch.setenv("BOOTSTRAP_REFERENCE_DATA", "false")
    monkeypatch.setenv("BOOTSTRAP_DEMO_DATA", "false")
    
    application = create_app()
    application.config.update(TESTING=True)
    application.config["SETTINGS"].expose_verification_links = True
    client: FlaskClient = application.test_client()

    yield {
        "application": application,
        "client": client,
    }

    close_connection()


@pytest.mark.e2e
def test_health_check(bootstrap_app):
    client = bootstrap_app["client"]
    response = client.get("/api/v1/health")

    assert response.get_json()["status"] == "ok"


@pytest.mark.e2e
def test_reference_data_api(bootstrap_app):
    client = bootstrap_app["client"]
    response = client.get("api/v1/meta/reference-data")

    assert "admin" in response.get_json()["roles"]
    assert "Assigned" in response.get_json()["report_statuses"]
    assert "Suspended" in response.get_json()["public_report_statuses"]


@pytest.mark.e2e
def test_register_user_api(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]

    payload = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.it",
        "password": "password123",
    }

    response_valid = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response_valid.status_code == 201

    data = response_valid.get_json()

    assert data["user"]["username"] == "mario"
    assert data["user"]["email"] == "mario@test.it"

    assert "verification_url" in data

    with application.app_context():
        session = get_session()
        saved = session.query(User).filter_by(username="mario").first()

        assert saved is not None
        assert saved.email == "mario@test.it"

    response_invalid = client.post(
        "/api/v1/auth/register",
        json={"username": "mario"},
    )

    assert response_invalid.status_code == 400



@pytest.mark.e2e
def test_verify_email_api(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]
    test_token = "abc-123-xyz"

    with application.app_context():
        session = get_session()

        user = User(
            username="tester",
            first_name="Nome",
            last_name="Cognome",
            email="test@example.com",
            password_hash="...",
            role="citizen"
        )
        session.add(user)
        session.commit()

        verification = EmailVerificationToken(
            token=test_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            is_used=False
        )
        session.add(verification)
        session.commit()

    response = client.get(f"api/v1/auth/verify/{test_token}")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Email verified."



@pytest.mark.e2e
def test_login_api(bootstrap_app):
    client = bootstrap_app["client"]

    payload_register = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.it",
        "password": "password123",
    }

    response_register = client.post(
        "/api/v1/auth/register",
        json=payload_register,
    )

    assert response_register.status_code == 201

    data = response_register.get_json()
    verification_url = data["verification_url"]

    client.get(verification_url)

    payload_login_1 = {
        "identifier": "mario",
        "password": "password123"
    }

    response_login_1 = client.post(
        "/api/v1/auth/login",
        json=payload_login_1
    )

    assert response_login_1.status_code == 200
    data_1 = response_login_1.get_json()

    assert data_1["user"]["username"] == "mario"

    payload_login_2 = {
        "identifier": "mario@test.it",
        "password": "password123"
    }

    response_login_2 = client.post(
        "/api/v1/auth/login",
        json=payload_login_2
    )

    assert response_login_2.status_code == 200
    data = response_login_2.get_json()

    assert data["user"]["username"] == "mario"

    payload_login_invalid = {
        "identifier": "alessandro",
        "password": "password123"
    }

    response_login_invalid = client.post(
        "/api/v1/auth/login",
        json=payload_login_invalid
    )

    assert response_login_invalid.status_code == 401


@pytest.mark.e2e
def test_logout_api(bootstrap_app):
    client = bootstrap_app["client"]

    payload_register = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.it",
        "password": "password123",
    }

    response_register = client.post(
        "/api/v1/auth/register",
        json=payload_register,
    )

    assert response_register.status_code == 201

    data = response_register.get_json()
    verification_url = data["verification_url"]

    client.get(verification_url)

    payload_login = {
        "identifier": "mario",
        "password": "password123"
    }

    response_login = client.post(
        "/api/v1/auth/login",
        json=payload_login
    )

    assert response_login.status_code == 200

    response_logout = client.post(
        "/api/v1/auth/logout"
    )

    assert response_logout.status_code == 200


@pytest.mark.e2e
def test_list_categories(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]

    with application.app_context():
        session = get_session()

        session.add(Category(name="Strade", is_active=True))
        session.add(Category(name="Illuminazione", is_active=True))
        session.add(Category(name="Salute", is_active=False))
        session.commit()

    response = client.get("/api/v1/categories")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    names = [c["name"] for c in data]

    assert "Strade" in names
    assert "Illuminazione" in names
    assert "Salute" not in names


@pytest.mark.e2e
def test_list_reports(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]
    with application.app_context():
        session = get_session()
        category=Category(name="Strade", is_active=True, id=3)
        category2=Category(name="Illuminazione", is_active=True, id=4)
        session.add(Report(id=1,title="buca",description="description",latitude=1,longitude=2,is_anonymous=False,status=ReportStatus.IN_PROGRESS,category=category))
        session.add(Report(id=2,title="lampione",description="description",latitude=6,longitude=8,is_anonymous=False,status=ReportStatus.IN_PROGRESS,category=category2))

        session.commit()
    response=client.get(f"/api/v1/reports")
    assert response.status_code == 200
    data=response.get_json()
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[1]["title"] == "lampione"


@pytest.mark.e2e
def test_create_report(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]
    form_data={
        "title": "lampione",
        "description": "description",
        "category_id" : 4,
        "latitude": 1,
        "longitude": 2,
        "is_anonymous": False,
        "photos" : (io.BytesIO(b"contenuto_finto_della_foto"), "test_image.png")


    }
    payload_register = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.it",
        "password": "password123",
    }
    with application.app_context():
        session = get_session()
        session.add(Category(name="Strade", is_active=True,id=4))
        session.commit()
    response_register = client.post(
        "/api/v1/auth/register",
        json=payload_register,
    )

    assert response_register.status_code == 201

    data = response_register.get_json()
    verification_url = data["verification_url"]

    client.get(verification_url)

    payload_login = {
        "identifier": "mario",
        "password": "password123"
    }

    response_login = client.post(
        "/api/v1/auth/login",
        json=payload_login
    )

    response=client.post(
        "/api/v1/reports",
        data=form_data,
    )
    assert response.status_code == 201
    assert response.get_json()["can_access_messages"]==False
    status_history= response.get_json()["status_history"]
    assert len(status_history) == 1


@pytest.mark.e2e
def test_exports_report(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]
    form_data={
        "title": "lampione",
        "description": "description",
        "category_id" : 4,
        "latitude": 1,
        "longitude": 2,
        "is_anonymous": False,
        "photos" : (io.BytesIO(b"contenuto_finto_della_foto"), "test_image.png")


    }
    payload_register = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.it",
        "password": "password123",
    }
    with application.app_context():
        session = get_session()
        session.add(Category(name="Strade", is_active=True,id=4))
        session.commit()
    response_register = client.post(
        "/api/v1/auth/register",
        json=payload_register,
    )

    assert response_register.status_code == 201

    data = response_register.get_json()
    verification_url = data["verification_url"]

    client.get(verification_url)

    payload_login = {
        "identifier": "mario",
        "password": "password123"
    }

    response_login = client.post(
        "/api/v1/auth/login",
        json=payload_login
    )

    response=client.post(
        "/api/v1/reports",
        data=form_data,
    )
    assert response.status_code == 201
    reports=client.get(f"/api/v1/reports")
    assert reports.status_code == 200



@pytest.mark.e2e
def test_report_detail(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]
    form_data = {
        "title": "lampione",
        "description": "description",
        "category_id": 4,
        "latitude": 1,
        "longitude": 2,
        "is_anonymous": False,
        "photos": (io.BytesIO(b"contenuto_finto_della_foto"), "test_image.png")

    }
    payload_register = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.it",
        "password": "password123",
    }
    with application.app_context():
        session = get_session()
        session.add(Category(name="Strade", is_active=True, id=4))
        session.commit()
    response_register = client.post(
        "/api/v1/auth/register",
        json=payload_register,
    )

    assert response_register.status_code == 201

    data = response_register.get_json()
    verification_url = data["verification_url"]

    client.get(verification_url)

    payload_login = {
        "identifier": "mario",
        "password": "password123"
    }

    response_login = client.post(
        "/api/v1/auth/login",
        json=payload_login
    )
    response = client.post(
        "/api/v1/reports",
        data=form_data,
    )

    id=response.get_json()["id"]
    report_detail=client.get(f"/api/v1/reports/{id}")
    assert report_detail.status_code == 200
    assert report_detail.get_json()["title"]=="lampione"


@pytest.mark.e2e
def test_follow_report(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]
    report = Report(
        id=123,
        title="lampione rotto",
        description="buio totale",
        category_id=4,
        latitude=1.0,
        longitude=2.0,
        is_anonymous=False,
        status=ReportStatus.IN_PROGRESS
    )


    payload_register = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.it",
        "password": "password123",
    }
    with application.app_context():
        session = get_session()
        session.add(Category(name="Strade", is_active=True, id=4))
        session.add(report)
        session.commit()
    response_register = client.post(
        "/api/v1/auth/register",
        json=payload_register,
    )

    assert response_register.status_code == 201

    data = response_register.get_json()
    verification_url = data["verification_url"]

    client.get(verification_url)

    payload_login = {
        "identifier": "mario",
        "password": "password123"
    }

    response_login = client.post(
        "/api/v1/auth/login",
        json=payload_login
    )



    report_detail = client.post(f"/api/v1/reports/123/follow")
    assert report_detail.status_code == 200
    assert report_detail.get_json()["title"] == "lampione rotto"


@pytest.mark.e2e
def test_unfollow_report(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]

    report = Report(
        id=123,
        title="lampione rotto",
        description="buio totale",
        category_id=4,
        latitude=1.0,
        longitude=2.0,
        is_anonymous=False,
        status=ReportStatus.IN_PROGRESS
    )


    payload_register = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.it",
        "password": "password123",
    }
    with application.app_context():
        session = get_session()
        session.add(Category(name="Strade", is_active=True, id=4))
        session.add(report)
        session.commit()
    response_register = client.post(
        "/api/v1/auth/register",
        json=payload_register,
    )

    assert response_register.status_code == 201

    data = response_register.get_json()
    verification_url = data["verification_url"]

    client.get(verification_url)

    payload_login = {
        "identifier": "mario",
        "password": "password123"
    }

    response_login = client.post(
        "/api/v1/auth/login",
        json=payload_login
    )



    report_detail = client.delete(f"/api/v1/reports/123/follow")
    assert report_detail.status_code == 200
    assert report_detail.get_json()["title"] == "lampione rotto"


@pytest.mark.e2e
def test_list_messages(bootstrap_app):
    client = bootstrap_app["client"]
    application = bootstrap_app["application"]

    payload_register = {
        "username": "mario",
        "first_name": "Mario",
        "last_name": "Rossi",
        "email": "mario@test.it",
        "password": "password123",
    }

    response_register = client.post(
        "/api/v1/auth/register",
        json=payload_register,
    )

    assert response_register.status_code == 201

    data = response_register.get_json()
    verification_url = data["verification_url"]

    client.get(verification_url)

    payload_login = {
        "identifier": "mario",
        "password": "password123"
    }

    response_login = client.post(
        "/api/v1/auth/login",
        json=payload_login
    )
    with application.app_context():
        session = get_session()
        session.add(Category(name="Strade", is_active=True, id=4))
        mario_user=session.query(User).filter_by(username="mario").first()
        mario_id=mario_user.id
        session.add(User(
        id=20,
        username="recipient_luca",
        first_name="Luca",
        last_name="Bianchi",
        email="luca.recipient@test.it",
        password_hash="scrypt:32768:8:1$fakehash",
        role=Role.OPERATOR,
        is_active=True,
        is_email_verified=True,
        email_notifications_enabled=True
    ))

        messaggio=Message(
        id=1,
        report_id=123,
        sender_id=mario_id,
        recipient_id=20,
        body="Ciao"
    )

        session.add(Report(
        id=123,
        title="lampione rotto",
        description="buio totale",
        category_id=4,
        latitude=1.0,
        longitude=2.0,
        reporter_id=mario_id,
        is_anonymous=False,
        status=ReportStatus.IN_PROGRESS,
        messages= [messaggio]
    ))
        session.commit()
    message_detail = client.get(f"/api/v1/reports/123/messages")
    assert message_detail.status_code == 200
    assert len(message_detail.get_json())==1