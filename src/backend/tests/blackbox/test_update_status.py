from __future__ import annotations

import pytest

from participium.services.report_service import ReportService
from participium.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from participium.models.enums import Role, ReportStatus
from participium.models.user import User
from participium.models.report import Report

ADMIN_USER = User(
    id=1,
    username="admin.boss",
    role=Role.ADMIN,
    is_active=True
)

OPERATOR_CAT_A = User(
    id=2,
    username="operator.a",
    role=Role.OPERATOR,
    is_active=True
)

CITIZEN_USER = User(
    id=3,
    username="citizen.mario",
    role=Role.CITIZEN,
    is_active=True
)

REPORT_NEW = Report(
    id=1,
    title="Buca in strada",
    status=ReportStatus.PENDING_APPROVAL,
    category_id=10
)


@pytest.fixture
def seed_report_data() -> None:
    """Popola il sistema con i report e gli utenti necessari per update_status."""
    pass


# TC-1: Successo nel cambio stato (Admin)
@pytest.mark.skip(reason="In progress.")
def test_update_status_success(seed_report_data: None) -> None:
    service = ReportService()
    
    updated_report = service.update_status(
        report_id=1,
        operator=ADMIN_USER,
        next_status_value=ReportStatus.ASSIGNED,
        note=None
    )
    
    assert isinstance(updated_report, Report)
    assert updated_report.status == ReportStatus.ASSIGNED

# TC-2: Errore Autorizzazione - Ruolo non idoneo (Citizen)
@pytest.mark.skip(reason="In progress.")
def test_update_status_error_unauthorized_role(seed_report_data: None) -> None:
    service = ReportService()
    
    with pytest.raises(AuthorizationError):
        service.update_status(
            report_id=1,
            operator=CITIZEN_USER,
            next_status_value=ReportStatus.ASSIGNED
        )

# TC-3: Errore Not Found - Report inesistente
@pytest.mark.skip(reason="In progress.")
def test_update_status_error_not_found(seed_report_data: None) -> None:
    service = ReportService()
    
    with pytest.raises(NotFoundError):
        service.update_status(
            report_id=999,
            operator=ADMIN_USER,
            next_status_value=ReportStatus.ASSIGNED
        )

# TC-4: Errore Autorizzazione - Operatore fuori categoria
@pytest.mark.skip(reason="In progress.")
def test_update_status_error_wrong_category(seed_report_data: None) -> None:
    service = ReportService()
    
    with pytest.raises(AuthorizationError):
        service.update_status(
            report_id=1,
            operator=OPERATOR_CAT_A,
            next_status_value=ReportStatus.IN_PROGRESS
        )

# TC-5: Errore Validazione - Stato non esistente
@pytest.mark.skip(reason="In progress.")
def test_update_status_error_invalid_status(seed_report_data: None) -> None:
    service = ReportService()
    
    with pytest.raises(ValidationError):
        service.update_status(
            report_id=1,
            operator=ADMIN_USER,
            next_status_value="STATO_INVENTATO"
        )

# TC-6: Errore Validazione - Nota mancante per Rejection
@pytest.mark.skip(reason="In progress.")
def test_update_status_error_missing_note_on_rejection(seed_report_data: None) -> None:
    service = ReportService()
    
    with pytest.raises(ValidationError):
        service.update_status(
            report_id=1,
            operator=ADMIN_USER,
            next_status_value=ReportStatus.REJECTED,
            note=None
        )

# TC-7: Successo Rejection con nota
@pytest.mark.skip(reason="In progress.")
def test_update_status_success_rejection(seed_report_data: None) -> None:
    service = ReportService()
    
    updated_report = service.update_status(
        report_id=1,
        operator=ADMIN_USER,
        next_status_value=ReportStatus.REJECTED,
        note="Foto non chiara"
    )
    
    assert updated_report.status == ReportStatus.REJECTED

# TC-8: Errore Validazione - Transizione workflow non permessa
@pytest.mark.skip(reason="In progress.")
def test_update_status_error_invalid_transition(seed_report_data: None) -> None:
    service = ReportService()
    
    with pytest.raises(ValidationError):
        service.update_status(
            report_id=1,
            operator=ADMIN_USER,
            next_status_value=ReportStatus.PENDING_APPROVAL
        )