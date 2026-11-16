from __future__ import annotations

import pytest

from participium.core.exceptions import ValidationError
from participium.models.enums import ReportStatus
from participium.core.status_flow import ensure_transition_allowed


@pytest.fixture
def seed_status_flow_data() -> None:
    pass


# Da PENDING_APPROVAL a <ReportStatus> (TC-1 - TC-6)
@pytest.mark.skip(reason="Disabled.")
def test_transitions_from_pending_approval(seed_status_flow_data: None) -> None:
    assert ensure_transition_allowed(ReportStatus.PENDING_APPROVAL, ReportStatus.PENDING_APPROVAL) is True
    assert ensure_transition_allowed(ReportStatus.PENDING_APPROVAL, ReportStatus.ASSIGNED) is True
    assert ensure_transition_allowed(ReportStatus.PENDING_APPROVAL, ReportStatus.REJECTED) is True

    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.PENDING_APPROVAL, ReportStatus.IN_PROGRESS)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.PENDING_APPROVAL, ReportStatus.SUSPENDED)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.PENDING_APPROVAL, ReportStatus.RESOLVED)


# Da ASSIGNED a <ReportStatus> (TC-7 - TC-12)
@pytest.mark.skip(reason="Disabled.")
def test_transitions_from_assigned(seed_status_flow_data: None) -> None:
    assert ensure_transition_allowed(ReportStatus.ASSIGNED, ReportStatus.ASSIGNED) is True
    assert ensure_transition_allowed(ReportStatus.ASSIGNED, ReportStatus.IN_PROGRESS) is True
    assert ensure_transition_allowed(ReportStatus.ASSIGNED, ReportStatus.SUSPENDED) is True
    assert ensure_transition_allowed(ReportStatus.ASSIGNED, ReportStatus.RESOLVED) is True

    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.ASSIGNED, ReportStatus.PENDING_APPROVAL)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.ASSIGNED, ReportStatus.REJECTED)


# Da IN_PROGRESS a <ReportStatus> (TC-13 - TC-18)
@pytest.mark.skip(reason="Disabled.")
def test_transitions_from_in_progress(seed_status_flow_data: None) -> None:
    assert ensure_transition_allowed(ReportStatus.IN_PROGRESS, ReportStatus.IN_PROGRESS) is True
    assert ensure_transition_allowed(ReportStatus.IN_PROGRESS, ReportStatus.SUSPENDED) is True
    assert ensure_transition_allowed(ReportStatus.IN_PROGRESS, ReportStatus.RESOLVED) is True

    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.IN_PROGRESS, ReportStatus.PENDING_APPROVAL)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.IN_PROGRESS, ReportStatus.ASSIGNED)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.IN_PROGRESS, ReportStatus.REJECTED)


# Da SUSPENDED a <ReportStatus> (TC-19 - TC-24)
@pytest.mark.skip(reason="Disabled.")
def test_transitions_from_suspended(seed_status_flow_data: None) -> None:
    assert ensure_transition_allowed(ReportStatus.SUSPENDED, ReportStatus.SUSPENDED) is True
    assert ensure_transition_allowed(ReportStatus.SUSPENDED, ReportStatus.IN_PROGRESS) is True
    assert ensure_transition_allowed(ReportStatus.SUSPENDED, ReportStatus.RESOLVED) is True

    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.SUSPENDED, ReportStatus.PENDING_APPROVAL)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.SUSPENDED, ReportStatus.ASSIGNED)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.SUSPENDED, ReportStatus.REJECTED)


# Da REJECTED a <ReportStatus> (TC-25 - TC-30)
@pytest.mark.skip(reason="Disabled.")
def test_transitions_from_rejected(seed_status_flow_data: None) -> None:
    assert ensure_transition_allowed(ReportStatus.REJECTED, ReportStatus.REJECTED) is True

    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.REJECTED, ReportStatus.PENDING_APPROVAL)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.REJECTED, ReportStatus.ASSIGNED)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.REJECTED, ReportStatus.IN_PROGRESS)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.REJECTED, ReportStatus.SUSPENDED)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.REJECTED, ReportStatus.RESOLVED)


# Da RESOLVED a <ReportStatus> (TC-31 - TC-36)
@pytest.mark.skip(reason="Disabled.")
def test_transitions_from_resolved(seed_status_flow_data: None) -> None:
    assert ensure_transition_allowed(ReportStatus.RESOLVED, ReportStatus.RESOLVED) is True

    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.RESOLVED, ReportStatus.PENDING_APPROVAL)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.RESOLVED, ReportStatus.ASSIGNED)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.RESOLVED, ReportStatus.IN_PROGRESS)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.RESOLVED, ReportStatus.SUSPENDED)
    with pytest.raises(ValidationError): ensure_transition_allowed(ReportStatus.RESOLVED, ReportStatus.REJECTED)
