import pytest
from unittest.mock import Mock
from datetime import datetime

from participium.controllers.report_controller import ReportController, ReportDetailContext
from participium.models.enums import ReportStatus


@pytest.fixture
def controller_bundle():
    report_service = Mock()
    messaging_service = Mock()
    notification_service = Mock()

    controller = ReportController(
        report_service=report_service,
        messaging_service=messaging_service,
        notification_service=notification_service
    )

    return {
        "controller": controller,
        "report_service": report_service,
        "messaging_service": messaging_service,
        "notification_service": notification_service,
    }


@pytest.mark.unit
def test_list_public_reports_defaults(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]

    reports = [Mock(), Mock()]
    report_service.list_public_reports.return_value = reports

    result = controller.list_public_reports()

    report_service.list_public_reports.assert_called_once_with(category_id=None, status=None, date_from=None,
                                                               date_to=None, sort="desc")
    assert result == reports


@pytest.mark.unit
def test_list_public_reports_custom(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]

    reports = [Mock()]
    date_from = datetime(2023, 1, 1)
    date_to = datetime(2023, 12, 31)
    report_service.list_public_reports.return_value = reports

    result = controller.list_public_reports(category_id=5, status=ReportStatus.PENDING_APPROVAL, date_from=date_from,
                                            date_to=date_to, sort="asc")

    report_service.list_public_reports.assert_called_once_with(category_id=5, status=ReportStatus.PENDING_APPROVAL,
                                                               date_from=date_from, date_to=date_to, sort="asc")
    assert result == reports


@pytest.mark.unit
def test_list_user_reports(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]

    user = Mock()
    reports = [Mock()]
    report_service.list_user_reports.return_value = reports

    result = controller.list_user_reports(user)

    report_service.list_user_reports.assert_called_once_with(user)
    assert result == reports


@pytest.mark.unit
def test_build_detail_context_with_user_and_access(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]
    messaging_service = controller_bundle["messaging_service"]
    notification_service = controller_bundle["notification_service"]

    report_id = 10
    user = Mock()
    user.id = 5
    report = Mock()
    report.id = 10
    report_service.get_accessible_report.return_value = report
    messaging_service.can_access_thread.return_value = True

    result = controller.build_detail_context(report_id, user)

    notification_service.mark_report_message_notifications_as_read.assert_called_once_with(5, 10)
    assert isinstance(result, ReportDetailContext)
    assert result.report == report
    assert result.can_access_messages is True


@pytest.mark.unit
def test_build_detail_context_with_user_no_access(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]
    messaging_service = controller_bundle["messaging_service"]
    notification_service = controller_bundle["notification_service"]

    report_id = 10
    user = Mock()
    report = Mock()
    report_service.get_accessible_report.return_value = report
    messaging_service.can_access_thread.return_value = False

    result = controller.build_detail_context(report_id, user)

    notification_service.mark_report_message_notifications_as_read.assert_not_called()
    assert isinstance(result, ReportDetailContext)
    assert result.report == report
    assert result.can_access_messages is False


@pytest.mark.unit
def test_build_detail_context_no_user(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]
    messaging_service = controller_bundle["messaging_service"]
    notification_service = controller_bundle["notification_service"]

    report_id = 10
    report = Mock()

    report_service.get_accessible_report.return_value = report
    messaging_service.can_access_thread.return_value = False

    result = controller.build_detail_context(report_id, user=None)

    notification_service.mark_report_message_notifications_as_read.assert_not_called()
    assert isinstance(result, ReportDetailContext)
    assert result.report == report
    assert result.can_access_messages is False


@pytest.mark.unit
def test_create_report(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]

    reporter = Mock()
    photos = [Mock(), Mock()]
    report = Mock()
    report_service.create_report.return_value = report

    result = controller.create_report(reporter=reporter, category_id=1, title="Fuga di gas", description="fuga di gas",
                                      latitude=45.0, longitude=9.0, photos=photos, is_anonymous=True)

    report_service.create_report.assert_called_once_with(reporter=reporter, category_id=1, title="Fuga di gas",
                                                         description="fuga di gas", latitude=45.0, longitude=9.0,
                                                         photos=photos, is_anonymous=True)
    assert result == report


@pytest.mark.unit
def test_follow_report(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]

    user = Mock()
    report = Mock()
    report_service.follow_report.return_value = report

    result = controller.follow_report(1, user)

    report_service.follow_report.assert_called_once_with(1, user)
    assert result == report


@pytest.mark.unit
def test_unfollow_report(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]

    user = Mock()
    report = Mock()
    report_service.unfollow_report.return_value = report

    result = controller.unfollow_report(1, user)

    report_service.unfollow_report.assert_called_once_with(1, user)
    assert result == report


@pytest.mark.unit
def test_export_rows(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]

    rows = [{"id": 1, "title": "Test"}]
    report_service.export_rows.return_value = rows

    result = controller.export_rows(category_id=2, status=ReportStatus.RESOLVED)

    report_service.export_rows.assert_called_once_with(category_id=2, status=ReportStatus.RESOLVED, date_from=None,
                                                       date_to=None, sort="desc")
    assert result == rows


@pytest.mark.unit
def test_list_messages(controller_bundle):
    controller = controller_bundle["controller"]
    messaging_service = controller_bundle["messaging_service"]

    report = Mock()
    user = Mock()
    messages = [Mock()]
    messaging_service.list_messages.return_value = messages

    result = controller.list_messages(report, user)

    messaging_service.list_messages.assert_called_once_with(report, user)
    assert result == messages


@pytest.mark.unit
def test_send_message(controller_bundle):
    controller = controller_bundle["controller"]
    messaging_service = controller_bundle["messaging_service"]

    report = Mock()
    sender = Mock()
    body = "A che punto sono i lavori?"
    message = Mock()
    messaging_service.send_message.return_value = message

    result = controller.send_message(report, sender, body)

    messaging_service.send_message.assert_called_once_with(report, sender, body)
    assert result == message
