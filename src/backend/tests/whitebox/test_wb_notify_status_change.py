from __future__ import annotations

import pytest
from unittest.mock import Mock, call

from participium.models.enums import NotificationType
from participium.services.notification_service import NotificationService
from participium.models.user import User
from participium.models.report import Report

pytestmark = pytest.mark.whitebox


# Structural tests for NotificationService.notify_status_change belong here.
# The current runnable smoke check is kept in test_wb_task06_smoke.py.


def _user(id) -> User:
    return User(id=id)


def _report(id, title) -> Report:
    return Report(id=id, title=title)


@pytest.fixture
def notification_service_bundle() -> dict[str, object]:
    session = Mock()
    notification_repository = Mock()
    email_gateway = Mock()
    create_notification_mock = Mock()
    service = NotificationService(
        session=session,
        notification_repository=notification_repository,
        email_gateway=email_gateway,
    )
    service.create_notification = create_notification_mock

    return {
        "service": service,
        "session": session,
        "notification_repository": notification_repository,
    }


def test_notify_status_change_empty(notification_service_bundle: dict[str, object]) -> None:

    report = _report(0, "test_report")
    body = "text"
    recipients = []

    service = notification_service_bundle["service"]

    service.notify_status_change(recipients, report, body)
    service.create_notification.assert_not_called()


def test_notify_status_change_single_valid(notification_service_bundle: dict[str, object]) -> None:

    user = _user(0)
    report = _report(0, "test_report")
    body = "text"
    recipients = [user]

    service = notification_service_bundle["service"]

    service.notify_status_change(recipients, report, body)
    service.create_notification.assert_called_once()
    service.create_notification.assert_called_once_with(
        user,
        NotificationType.STATUS_CHANGE,
        "Report #0 status updated",
        body,
        report=report
    )


def test_notify_status_change_mixed_case(notification_service_bundle: dict[str, object]) -> None:
    user1 = _user(1)
    user2 = _user(2)
    report = _report(0, "test_report")
    body = "text"
    recipients = [user1, None, user1, user2]

    service = notification_service_bundle["service"]

    service.notify_status_change(recipients, report, body)

    assert service.create_notification.call_count == 2

    service.create_notification.assert_has_calls([
        call(user1, NotificationType.STATUS_CHANGE, "Report #0 status updated", "text", report=report),
        call(user2, NotificationType.STATUS_CHANGE, "Report #0 status updated", "text", report=report),
    ], any_order=False)
