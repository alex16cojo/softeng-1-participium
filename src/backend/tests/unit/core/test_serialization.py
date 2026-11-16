from __future__ import annotations

from datetime import datetime

import pytest

from participium.core.serialization import (
    _media_url,
    _serialize_party,
    _serialize_reporter,
    serialize_category,
    serialize_message,
    serialize_notification,
    serialize_photo,
    serialize_report_detail,
    serialize_report_summary,
    serialize_user,
)
from participium.models.category import Category
from participium.models.enums import ReportStatus, NotificationType, Role
from participium.models.message import Message
from participium.models.notification import Notification
from participium.models.report import Report, ReportPhoto
from participium.models.user import User


@pytest.fixture
def category() -> Category:
    return Category(
        id=1,
        name="Road Maintenance",
        is_active=True,
        created_at=datetime(2024, 1, 1),
    )


@pytest.fixture
def user(category) -> User:
    return User(
        id=1,
        username="mario",
        first_name="Mario",
        last_name="Rossi",
        email="mario@test.it",
        role=Role.CITIZEN,
        category=category,
        category_id=category.id,
        is_active=True,
        is_email_verified=True,
        email_notifications_enabled=True,
        profile_picture_path="profiles/mario.jpg",
        created_at=datetime(2024, 1, 1),
    )


@pytest.fixture
def operator(category) -> User:
    return User(
        id=2,
        username="operator",
        first_name="Anna",
        last_name="Verdi",
        email="operator@test.it",
        role=Role.OPERATOR,
        category=category,
        category_id=category.id,
        is_active=True,
        is_email_verified=True,
        email_notifications_enabled=True,
        created_at=datetime(2024, 1, 1),
    )


@pytest.fixture
def admin() -> User:
    return User(
        id=3,
        username="admin",
        first_name="Admin",
        last_name="User",
        email="admin@test.it",
        role=Role.ADMIN,
        is_active=True,
        is_email_verified=True,
        email_notifications_enabled=True,
        created_at=datetime(2024, 1, 1),
    )


@pytest.fixture
def photo() -> ReportPhoto:
    return ReportPhoto(
        id=1,
        file_path="reports/photo.jpg",
        original_filename="photo.jpg",
        content_type="image/jpeg",
    )


@pytest.fixture
def message(user) -> Message:
    return Message(
        id=1,
        report_id=1,
        body="Test message",
        sender=user,
        recipient=user,
        created_at=datetime(2024, 1, 1),
    )


@pytest.fixture
def notification() -> Notification:
    return Notification(
        id=1,
        type=NotificationType.STATUS_CHANGE,
        title="New update",
        body="Report updated",
        report_id=1,
        is_read=False,
        created_at=datetime(2024, 1, 1),
    )


@pytest.fixture
def report(user, category, photo) -> Report:
    return Report(
        id=1,
        title="Broken streetlight",
        description="Lamp not working",
        category=category,
        category_id=category.id,
        reporter=user,
        reporter_id=user.id,
        status=ReportStatus.ASSIGNED,
        is_anonymous=False,
        photos=[photo],
        status_history=[],
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 2),
    )


def test_serialize_user(user):
    data = serialize_user(user)

    assert data["username"] == "mario"
    assert data["email"] == "mario@test.it"
    assert data["role"] == "citizen"
    assert data["profile_picture_url"] == "/static/uploads/profiles/mario.jpg"


def test_serialize_category(category):
    data = serialize_category(category)

    assert data["name"] == "Road Maintenance"
    assert data["is_active"] is True


def test_serialize_photo(photo):
    data = serialize_photo(photo)

    assert data["file_path"] == "reports/photo.jpg"
    assert data["url"] == "/static/uploads/reports/photo.jpg"


def test_serialize_notification(notification):
    data = serialize_notification(notification)

    assert data["type"] == "status_change"
    assert data["title"] == "New update"
    assert data["body"] == "Report updated"
    assert data["is_read"] is False


def test_serialize_message(message):
    data = serialize_message(message)

    assert data["body"] == "Test message"
    assert data["sender"]["display_name"] == "Mario Rossi"


def test_serialize_report_summary(report):
    data = serialize_report_summary(report)

    assert data["title"] == "Broken streetlight"
    assert data["status"] == "Assigned"
    assert data["is_anonymous"] is False
    assert data["reporter"]["display_name"] == "Mario Rossi"


def test_serialize_report_detail(report):
    data = serialize_report_detail(report, include_messages=True)

    assert data["can_access_messages"] is True
    assert "status_history" in data
    assert "messages" in data


def test_media_url():
    assert _media_url("file.jpg") == "/static/uploads/file.jpg"
    assert _media_url(None) is None


def test_serialize_party(user):
    data = _serialize_party(user)

    assert data["display_name"] == "Mario Rossi"
    assert data["role"] == "citizen"


def test_serialize_party_deleted_user():
    data = _serialize_party(None)

    assert data["display_name"] == "Deleted User"
    assert data["id"] is None


def test_anonymous_report_hides_reporter(report):
    report.is_anonymous = True

    data = serialize_report_summary(report)

    assert data["reporter"]["display_name"] == "Anonymous Citizen"


def test_admin_can_see_anonymous_reporter(report, admin):
    report.is_anonymous = True

    data = serialize_report_summary(report, viewer=admin)

    assert data["reporter"]["display_name"] == "Mario Rossi"


def test_operator_same_category_can_see_anonymous_reporter(report, operator):
    report.is_anonymous = True

    data = serialize_report_summary(report, viewer=operator)

    assert data["reporter"]["display_name"] == "Mario Rossi"


def test_report_owner_can_see_own_identity(report, user):
    report.is_anonymous = True

    data = serialize_report_summary(report, viewer=user)

    assert data["reporter"]["display_name"] == "Mario Rossi"


def test_serialize_reporter_anonymous(report, user):
    report.is_anonymous = True

    anonymous_user = User(
        id=999,
        username="luigi",
        first_name="Luigi",
        last_name="Verdi",
        email="luigi@test.it",
        role=Role.CITIZEN,
        category_id=99,
        is_active=True,
        is_email_verified=True,
    )

    result = _serialize_reporter(report, anonymous_user)

    assert result == {
        "display_name": "Anonymous Citizen",
        "id": None,
    }