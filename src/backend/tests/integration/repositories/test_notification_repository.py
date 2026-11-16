from __future__ import annotations

from datetime import datetime

import pytest

from participium.database import close_connection, create_all, get_session, open_connection
from participium.models.enums import NotificationType
from participium.models.notification import Notification
from participium.models.report import Report
from participium.models.user import User
from participium.repositories.notification_repository import NotificationRepository


def _user(user_id, username):
    return User(id=user_id, username=username, first_name=username, last_name="test", email=f"{username}@mail.com", password_hash="pass")


def _report(report_id):
    r = Report(id=report_id, title=f"report{report_id}", description="desc", latitude=1.0, longitude=1.0, is_anonymous=False, reporter_id=1, category_id=1)
    return r


def _notification(notification_id, user_id, report_id, type_, title, is_read=False):
    n = Notification(id=notification_id, user_id=user_id, report_id=report_id, type=type_, title=title, body="body", is_read=is_read)
    return n


@pytest.fixture
def init_session(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    open_connection()
    create_all()
    session = get_session()
    yield session
    close_connection()


@pytest.fixture
def populate_db(init_session):
    u1 = _user(1, "gianni")
    u2 = _user(2, "franco")
    r1 = _report(1)

    n1 = _notification(1, 1, 1, NotificationType.MESSAGE, "msg1", False)
    n2 = _notification(2, 1, 1, NotificationType.MESSAGE, "msg2", True)
    n3 = _notification(3, 1, 1, NotificationType.STATUS_CHANGE, "status", False)
    n4 = _notification(4, 2, 1, NotificationType.MESSAGE, "msg3", False)

    n1.created_at = datetime(2025, 1, 1)
    n2.created_at = datetime(2025, 2, 1)
    n3.created_at = datetime(2025, 3, 1)
    n4.created_at = datetime(2025, 4, 1)

    init_session.add_all([u1, u2, r1, n1, n2, n3, n4])
    init_session.commit()

    return init_session


@pytest.fixture
def init_repository(populate_db):
    return NotificationRepository(populate_db)


@pytest.mark.integration
def test_notification_add(init_repository):
    repository = init_repository

    notification = _notification(5, 1, 1, NotificationType.MESSAGE, "new")

    repository.add(notification)
    repository.session.commit()

    saved = repository.get_by_id(5)

    assert saved is not None
    assert saved.title == "new"


@pytest.mark.integration
def test_notification_get_by_id(init_repository):
    repository = init_repository

    notification1 = repository.get_by_id(1)
    notification2 = repository.get_by_id(99)

    assert notification1.title == "msg1"
    assert notification2 is None


@pytest.mark.integration
def test_notification_list_for_user(init_repository):
    repository = init_repository

    notifications = repository.list_for_user(1)

    ids = [n.id for n in notifications]

    assert ids == [3, 2, 1]


@pytest.mark.integration
def test_notification_list_unread_message_notifications(init_repository):
    repository = init_repository

    notifications = repository.list_unread_message_notifications(1)

    ids = [n.id for n in notifications]

    assert ids == [1]


@pytest.mark.integration
def test_notification_list_unread_message_notifications_with_report(init_repository):
    repository = init_repository

    notifications = repository.list_unread_message_notifications(1, 1)

    ids = [n.id for n in notifications]

    assert ids == [1]


@pytest.mark.integration
def test_notification_list_unread_message_notifications_empty(init_repository):
    repository = init_repository

    notifications = repository.list_unread_message_notifications(2, 99)

    assert notifications == []


@pytest.mark.integration
def test_notification_delete_for_user(init_repository):
    repository = init_repository

    repository.delete_for_user(1)
    repository.session.commit()

    notifications1 = repository.list_for_user(1)
    notifications2 = repository.list_for_user(2)

    assert notifications1 == []
    assert len(notifications2) == 1
    assert notifications2[0].id == 4