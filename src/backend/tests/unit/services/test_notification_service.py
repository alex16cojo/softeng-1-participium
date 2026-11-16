from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from participium.core.exceptions import AuthorizationError, NotFoundError
from participium.models.enums import NotificationType
from participium.models.notification import Notification
from participium.models.report import Report
from participium.models.user import User
from participium.services.notification_service import NotificationService


# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def make_service():
    def _make():
        return NotificationService(
            session=MagicMock(),
            notification_repository=MagicMock(),
            email_gateway=MagicMock(),
        )

    return _make


@pytest.fixture
def sample_user():
    return User(
        id=1,
        username="mario",
        email="mario@example.com",
        email_notifications_enabled=True,
    )


@pytest.fixture
def sample_report():
    return Report(
        id=99,
    )


@pytest.fixture
def sample_notification():
    return Notification(
        id=10,
        user_id=1,
        report_id=99,
        type=NotificationType.MESSAGE,
        title="Test",
        body="Body",
        is_read=False,
    )


# -------------------------
# Tests: create_notification
# -------------------------

def test_create_notification_user_none(make_service, sample_report):
    service = make_service()

    result = service.create_notification(
        None,
        NotificationType.MESSAGE,
        "Title",
        "Body",
        report=sample_report,
    )

    assert result is None

    service.notification_repository.add.assert_not_called()
    service.email_gateway.send.assert_not_called()


def test_create_notification_success(make_service, sample_user, sample_report):
    service = make_service()

    notification = service.create_notification(
        sample_user,
        NotificationType.STATUS_CHANGE,
        "Status changed",
        "Your report was updated",
        report=sample_report,
    )

    assert notification.user_id == sample_user.id
    assert notification.report_id == sample_report.id
    assert notification.type == NotificationType.STATUS_CHANGE
    assert notification.is_read is False

    service.notification_repository.add.assert_called_once_with(notification)
    service.email_gateway.send.assert_called_once_with(
        sample_user.email,
        "Status changed",
        "Your report was updated",
    )


def test_create_notification_without_report(make_service, sample_user):
    service = make_service()

    notification = service.create_notification(
        sample_user,
        NotificationType.MESSAGE,
        "Message",
        "Hello",
    )

    assert notification.report_id is None


def test_create_notification_email_disabled(make_service, sample_user):
    service = make_service()

    sample_user.email_notifications_enabled = False

    service.create_notification(
        sample_user,
        NotificationType.MESSAGE,
        "Title",
        "Body",
    )

    service.email_gateway.send.assert_not_called()


def test_create_notification_email_failure_is_swallowed(make_service, sample_user):
    service = make_service()

    service.email_gateway.send.side_effect = Exception("SMTP failed")

    notification = service.create_notification(
        sample_user,
        NotificationType.MESSAGE,
        "Title",
        "Body",
    )

    assert notification is not None

    service.notification_repository.add.assert_called_once()


# -------------------------
# Tests: notify_status_change
# -------------------------

def test_notify_status_change_creates_notifications(make_service, sample_user, sample_report):
    service = make_service()

    another_user = User(
        id=2,
        username="luigi",
        email="luigi@example.com",
        email_notifications_enabled=True,
    )

    service.create_notification = MagicMock()

    recipients = [sample_user, another_user]

    service.notify_status_change(
        recipients,
        sample_report,
        "Status updated",
    )

    assert service.create_notification.call_count == 2


def test_notify_status_change_skips_duplicates_and_none(make_service, sample_user, sample_report):
    service = make_service()

    service.create_notification = MagicMock()

    recipients = [
        sample_user,
        None,
        sample_user,
    ]

    service.notify_status_change(
        recipients,
        sample_report,
        "Status updated",
    )

    service.create_notification.assert_called_once()


# -------------------------
# Tests: notify_new_message
# -------------------------

def test_notify_new_message(make_service, sample_user, sample_report):
    service = make_service()

    service.create_notification = MagicMock()

    service.notify_new_message(
        sample_user,
        sample_report,
        "Giulia",
        "Hello there",
    )

    service.create_notification.assert_called_once_with(
        sample_user,
        NotificationType.MESSAGE,
        f"New message on report #{sample_report.id}",
        "Giulia: Hello there",
        report=sample_report,
    )


# -------------------------
# Tests: list_notifications
# -------------------------

def test_list_notifications(make_service):
    service = make_service()

    notifications = [MagicMock(), MagicMock()]

    service.notification_repository.list_for_user.return_value = notifications

    result = service.list_notifications(1)

    assert result == notifications

    service.notification_repository.list_for_user.assert_called_once_with(1)


# -------------------------
# Tests: count_unread_message_notifications_by_report
# -------------------------

def test_count_unread_message_notifications_by_report(make_service):
    service = make_service()

    notifications = [
        Notification(report_id=1),
        Notification(report_id=1),
        Notification(report_id=2),
        Notification(report_id=None),
    ]

    service.notification_repository.list_unread_message_notifications.return_value = notifications

    counts = service.count_unread_message_notifications_by_report(1)

    assert counts == {
        1: 2,
        2: 1,
    }


# -------------------------
# Tests: mark_report_message_notifications_as_read
# -------------------------

def test_mark_report_message_notifications_as_read(make_service):
    service = make_service()

    notifications = [
        Notification(is_read=False),
        Notification(is_read=False),
    ]

    service.notification_repository.list_unread_message_notifications.return_value = notifications

    count = service.mark_report_message_notifications_as_read(
        user_id=1,
        report_id=99,
    )

    assert count == 2
    assert all(notification.is_read for notification in notifications)

    service.session.commit.assert_called_once()


def test_mark_report_message_notifications_as_read_empty(make_service):
    service = make_service()

    service.notification_repository.list_unread_message_notifications.return_value = []

    count = service.mark_report_message_notifications_as_read(
        user_id=1,
        report_id=99,
    )

    assert count == 0

    service.session.commit.assert_not_called()


# -------------------------
# Tests: get_user_notification
# -------------------------

def test_get_user_notification_success(make_service, sample_notification):
    service = make_service()

    service.notification_repository.get_by_id.return_value = sample_notification

    result = service.get_user_notification(1, 10)

    assert result == sample_notification


def test_get_user_notification_not_found(make_service):
    service = make_service()

    service.notification_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_user_notification(1, 10)


def test_get_user_notification_wrong_user(make_service, sample_notification):
    service = make_service()

    sample_notification.user_id = 999

    service.notification_repository.get_by_id.return_value = sample_notification

    with pytest.raises(AuthorizationError):
        service.get_user_notification(1, 10)


# -------------------------
# Tests: mark_as_read
# -------------------------

def test_mark_as_read(make_service, sample_notification):
    service = make_service()

    result = service.mark_as_read(sample_notification)

    assert result.is_read is True

    service.session.commit.assert_called_once()