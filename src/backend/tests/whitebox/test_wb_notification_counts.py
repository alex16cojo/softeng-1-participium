from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from participium.services.notification_service import NotificationService


pytestmark = pytest.mark.whitebox


@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def service(mock_repo):
    return NotificationService(notification_repository=mock_repo)

# Path1
def test_count_unread_empty_list(service, mock_repo):
    mock_repo.list_unread_message_notifications.return_value = []
    result = service.count_unread_message_notifications_by_report(user_id=123)
    assert result == {}
    mock_repo.list_unread_message_notifications.assert_called_once_with(user_id=123)

# Path2
def test_count_unread_with_none_report_id(service, mock_repo):
    notification_none = MagicMock()
    notification_none.report_id = None
    mock_repo.list_unread_message_notifications.return_value = [notification_none]
    
    result = service.count_unread_message_notifications_by_report(user_id=123)
    
    assert result == {}

# Path3
def test_count_unread_full_coverage_and_aggregation(service, mock_repo):
    
    n1 = MagicMock(report_id=10)
    n2 = MagicMock(report_id=10)
    n3 = MagicMock(report_id=20)
    mock_repo.list_unread_message_notifications.return_value = [n1, n2, n3]
    result = service.count_unread_message_notifications_by_report(user_id=123)
    
    assert result == {10: 2, 20: 1}
    assert len(result) == 2