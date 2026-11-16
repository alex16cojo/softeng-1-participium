from __future__ import annotations

import pytest

from participium.models.enums import NotificationType, ReportStatus
from participium.models.user import User
from participium.models.report import Report
from participium.models.notification import Notification
from participium.services.notification_service import NotificationService

RECIPIENT_USER = User(
    id=1,
    username="mario.rossi",
    email="mario.rossi18@email.com",
    is_active=True
)

RELATED_REPORT = Report(
    id=10,
    title="Lampione rotto",
    status=ReportStatus.PENDING_APPROVAL
)

@pytest.fixture
def seed_notification_data() -> None:
    """Non realizzato"""
    pass

# TC-1: Creazione notifica standard valida
@pytest.mark.skip(reason="In progress.")
def test_create_notification_success(seed_notification_data: None) -> None:
    service = NotificationService()
    
    notification = service.create_notification(
        user=RECIPIENT_USER,
        notification_type=NotificationType.STATUS_CHANGE,
        title="Cambio Stato",
        body="La tua segnalazione è stata approvata.",
        report=RELATED_REPORT
    )
    assert isinstance(notification, Notification)
    assert notification.user_id == RECIPIENT_USER.id
    assert notification.report_id == RELATED_REPORT.id
    assert notification.title == "Cambio Stato"

# TC-2: Se Utente nullo ritorna None
@pytest.mark.skip(reason="In progress.")
def test_create_notification_null_user(seed_notification_data: None) -> None:
    service = NotificationService()
    
    notification = service.create_notification(
        user=None,
        notification_type=NotificationType.STATUS_CHANGE,
        title="Update",
        body="Message",
        report=RELATED_REPORT
    )
    assert notification is None

# TC-3: Notifica di sistema senza il report associato
@pytest.mark.skip(reason="In progress.")
def test_create_notification_no_report(seed_notification_data: None) -> None:
    service = NotificationService()
    
    notification = service.create_notification(
        user=RECIPIENT_USER,
        notification_type=NotificationType.SYSTEM,
        title="Manutenzione",
        body="Il sistema sarà offline stanotte.",
        report=None
    )
    assert isinstance(notification, Notification)
    assert notification.report_id is None
    assert notification.type == NotificationType.SYSTEM

# TC-4: Test con titolo vuoto
@pytest.mark.skip(reason="In progress.")
def test_create_notification_empty_title(seed_notification_data: None) -> None:
    service = NotificationService()
    
    notification = service.create_notification(
        user=RECIPIENT_USER,
        notification_type=NotificationType.MESSAGE,
        title="",
        body="Contenuto del messaggio"
    )
    assert isinstance(notification, Notification)
    assert notification.title == ""
    assert notification.body == "Contenuto del messaggio"


# TC-5: Test con body vuoto
@pytest.mark.skip(reason="In progress.")
def test_create_notification_empty_body(seed_notification_data: None) -> None:
    service = NotificationService()
    
    notification = service.create_notification(
        user=RECIPIENT_USER,
        notification_type=NotificationType.STATUS_CHANGE,
        title="Notifica senza testo",
        body=""
    )
    assert isinstance(notification, Notification)
    assert notification.title == "Notifica senza testo"
    assert notification.body == ""