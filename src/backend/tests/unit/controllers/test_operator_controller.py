import pytest
from unittest.mock import Mock

from participium.controllers.operator_controller import OperatorController, OperatorDashboardContext
from participium.models.enums import Role


@pytest.fixture
def controller_bundle():
    report_service = Mock()
    notification_service = Mock()

    controller = OperatorController(
        report_service=report_service,
        notification_service=notification_service
    )

    return {
        "controller": controller,
        "report_service": report_service,
        "notification_service": notification_service,
    }


@pytest.mark.unit
def test_build_dashboard_for_admin(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]
    notification_service = controller_bundle["notification_service"]

    admin_user = Mock()
    admin_user.id = 1
    admin_user.role = Role.ADMIN

    filters = {"status": "OPEN"}

    pending_reports = [Mock(), Mock()]
    assigned_reports = [Mock()]
    unread_message_count = {101: 2}
    report_service.list_pending_reports.return_value = pending_reports
    report_service.list_operator_reports.return_value = assigned_reports
    notification_service.count_unread_message_notifications_by_report.return_value = unread_message_count

    result = controller.build_dashboard(admin_user, filters)

    report_service.list_pending_reports.assert_called_once_with({"status": "OPEN"})
    report_service.list_operator_reports.assert_called_once_with(admin_user)
    notification_service.count_unread_message_notifications_by_report.assert_called_once_with(1)

    assert isinstance(result, OperatorDashboardContext)
    assert result.pending_reports == pending_reports
    assert result.assigned_reports == assigned_reports
    assert result.unread_message_counts == unread_message_count


@pytest.mark.unit
def test_build_dashboard_for_operator_no_filters(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]
    notification_service = controller_bundle["notification_service"]

    operator_user = Mock()
    operator_user.id = 2
    operator_user.role = Role.OPERATOR
    operator_user.category_id = 5

    pending_reports = [Mock()]
    assigned_reports = []
    unread_message_count = {}
    report_service.list_pending_reports.return_value = pending_reports
    report_service.list_operator_reports.return_value = assigned_reports
    notification_service.count_unread_message_notifications_by_report.return_value = unread_message_count

    result = controller.build_dashboard(operator_user)

    expected_filters = {"category_id": 5}
    report_service.list_pending_reports.assert_called_once_with(expected_filters)
    assert result.pending_reports == pending_reports
    assert result.assigned_reports == assigned_reports


@pytest.mark.unit
def test_build_dashboard_for_other_role(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]
    notification_service = controller_bundle["notification_service"]

    other_user = Mock()
    other_user.id = 3
    other_user.role = Role.CITIZEN

    assigned_reports = []
    unread_message_count = {}
    report_service.list_operator_reports.return_value = assigned_reports
    notification_service.count_unread_message_notifications_by_report.return_value = unread_message_count

    result = controller.build_dashboard(other_user)

    report_service.list_pending_reports.assert_not_called()
    assert result.pending_reports == []
    assert result.assigned_reports == assigned_reports


@pytest.mark.unit
def test_assign_report(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]

    report_id = 15
    operator = Mock()
    report = Mock()
    report_service.assign_report.return_value = report

    result = controller.assign_report(report_id, operator)

    report_service.assign_report.assert_called_once_with(report_id, operator)
    assert result == report


@pytest.mark.unit
def test_update_status(controller_bundle):
    controller = controller_bundle["controller"]
    report_service = controller_bundle["report_service"]

    report_id = 15
    operator = Mock()
    next_status = "In_progress"
    note = "Nota"
    report = Mock()
    report_service.update_status.return_value = report

    result = controller.update_status(report_id, operator, next_status, note)

    report_service.update_status.assert_called_once_with(report_id, operator, next_status, note)
    assert result == report
