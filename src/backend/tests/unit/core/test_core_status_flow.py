import pytest

from participium.core.exceptions import ValidationError
from participium.core.status_flow import ensure_transition_allowed
from participium.models.enums import ReportStatus


class TestEnsureTransitionAllowed:
    """Test suite for ensure_transition_allowed function."""

    # Self-transitions (should always be allowed)
    def test_self_transition_pending_approval(self):
        """Test that a report can stay in Pending Approval status."""
        result = ensure_transition_allowed(
            ReportStatus.PENDING_APPROVAL, ReportStatus.PENDING_APPROVAL
        )
        assert result is True

    def test_self_transition_assigned(self):
        """Test that a report can stay in Assigned status."""
        result = ensure_transition_allowed(ReportStatus.ASSIGNED, ReportStatus.ASSIGNED)
        assert result is True

    def test_self_transition_in_progress(self):
        """Test that a report can stay in In Progress status."""
        result = ensure_transition_allowed(
            ReportStatus.IN_PROGRESS, ReportStatus.IN_PROGRESS
        )
        assert result is True

    def test_self_transition_suspended(self):
        """Test that a report can stay in Suspended status."""
        result = ensure_transition_allowed(ReportStatus.SUSPENDED, ReportStatus.SUSPENDED)
        assert result is True

    def test_self_transition_rejected(self):
        """Test that a report can stay in Rejected status."""
        result = ensure_transition_allowed(ReportStatus.REJECTED, ReportStatus.REJECTED)
        assert result is True

    def test_self_transition_resolved(self):
        """Test that a report can stay in Resolved status."""
        result = ensure_transition_allowed(ReportStatus.RESOLVED, ReportStatus.RESOLVED)
        assert result is True

    # Valid transitions from PENDING_APPROVAL
    def test_transition_pending_approval_to_assigned(self):
        """Test valid transition from Pending Approval to Assigned."""
        result = ensure_transition_allowed(
            ReportStatus.PENDING_APPROVAL, ReportStatus.ASSIGNED
        )
        assert result is True

    def test_transition_pending_approval_to_rejected(self):
        """Test valid transition from Pending Approval to Rejected."""
        result = ensure_transition_allowed(
            ReportStatus.PENDING_APPROVAL, ReportStatus.REJECTED
        )
        assert result is True

    # Valid transitions from ASSIGNED
    def test_transition_assigned_to_in_progress(self):
        """Test valid transition from Assigned to In Progress."""
        result = ensure_transition_allowed(
            ReportStatus.ASSIGNED, ReportStatus.IN_PROGRESS
        )
        assert result is True

    def test_transition_assigned_to_suspended(self):
        """Test valid transition from Assigned to Suspended."""
        result = ensure_transition_allowed(
            ReportStatus.ASSIGNED, ReportStatus.SUSPENDED
        )
        assert result is True

    def test_transition_assigned_to_resolved(self):
        """Test valid transition from Assigned to Resolved."""
        result = ensure_transition_allowed(
            ReportStatus.ASSIGNED, ReportStatus.RESOLVED
        )
        assert result is True

    # Valid transitions from IN_PROGRESS
    def test_transition_in_progress_to_suspended(self):
        """Test valid transition from In Progress to Suspended."""
        result = ensure_transition_allowed(
            ReportStatus.IN_PROGRESS, ReportStatus.SUSPENDED
        )
        assert result is True

    def test_transition_in_progress_to_resolved(self):
        """Test valid transition from In Progress to Resolved."""
        result = ensure_transition_allowed(
            ReportStatus.IN_PROGRESS, ReportStatus.RESOLVED
        )
        assert result is True

    # Valid transitions from SUSPENDED
    def test_transition_suspended_to_in_progress(self):
        """Test valid transition from Suspended to In Progress."""
        result = ensure_transition_allowed(
            ReportStatus.SUSPENDED, ReportStatus.IN_PROGRESS
        )
        assert result is True

    def test_transition_suspended_to_resolved(self):
        """Test valid transition from Suspended to Resolved."""
        result = ensure_transition_allowed(
            ReportStatus.SUSPENDED, ReportStatus.RESOLVED
        )
        assert result is True

    # Invalid transitions
    def test_invalid_transition_pending_approval_to_in_progress(self):
        """Test that transition from Pending Approval to In Progress is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(
                ReportStatus.PENDING_APPROVAL, ReportStatus.IN_PROGRESS
            )
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_pending_approval_to_suspended(self):
        """Test that transition from Pending Approval to Suspended is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(
                ReportStatus.PENDING_APPROVAL, ReportStatus.SUSPENDED
            )
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_pending_approval_to_resolved(self):
        """Test that transition from Pending Approval to Resolved is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(
                ReportStatus.PENDING_APPROVAL, ReportStatus.RESOLVED
            )
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_assigned_to_rejected(self):
        """Test that transition from Assigned to Rejected is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(ReportStatus.ASSIGNED, ReportStatus.REJECTED)
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_in_progress_to_assigned(self):
        """Test that transition from In Progress to Assigned is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(
                ReportStatus.IN_PROGRESS, ReportStatus.ASSIGNED
            )
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_in_progress_to_rejected(self):
        """Test that transition from In Progress to Rejected is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(
                ReportStatus.IN_PROGRESS, ReportStatus.REJECTED
            )
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_suspended_to_assigned(self):
        """Test that transition from Suspended to Assigned is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(ReportStatus.SUSPENDED, ReportStatus.ASSIGNED)
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_rejected_to_assigned(self):
        """Test that transition from Rejected to Assigned is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(ReportStatus.REJECTED, ReportStatus.ASSIGNED)
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_rejected_to_in_progress(self):
        """Test that transition from Rejected to In Progress is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(
                ReportStatus.REJECTED, ReportStatus.IN_PROGRESS
            )
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_resolved_to_assigned(self):
        """Test that transition from Resolved to Assigned is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(ReportStatus.RESOLVED, ReportStatus.ASSIGNED)
        assert "not allowed" in str(exc_info.value)

    def test_invalid_transition_resolved_to_in_progress(self):
        """Test that transition from Resolved to In Progress is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(
                ReportStatus.RESOLVED, ReportStatus.IN_PROGRESS
            )
        assert "not allowed" in str(exc_info.value)

    def test_error_message_format(self):
        """Test that error message includes both status values."""
        with pytest.raises(ValidationError) as exc_info:
            ensure_transition_allowed(ReportStatus.REJECTED, ReportStatus.ASSIGNED)
        error_msg = str(exc_info.value)
        assert "Rejected" in error_msg
        assert "Assigned" in error_msg
