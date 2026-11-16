from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from participium.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report
from participium.models.user import User
from participium.services.report_service import ReportService


# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def make_service():
    def _make():
        return ReportService(
            session=MagicMock(),
            report_repository=MagicMock(),
            category_repository=MagicMock(),
            storage_service=MagicMock(),
            notification_service=MagicMock(),
        )

    return _make


@pytest.fixture
def citizen():
    return User(id=1, username="citizen", role=Role.CITIZEN)


@pytest.fixture
def operator():
    return User(id=2, username="operator", role=Role.OPERATOR, category_id=10)


@pytest.fixture
def admin():
    return User(id=3, username="admin", role=Role.ADMIN)


@pytest.fixture
def category():
    category = MagicMock()
    category.id = 10
    category.name = "Roads"
    category.is_active = True
    return category


@pytest.fixture
def report(citizen, category):
    report = Report(
        id=99,
        title="Broken road",
        description="Description",
        latitude=45.0,
        longitude=9.0,
        reporter_id=citizen.id,
        category_id=10,
        status=ReportStatus.PENDING_APPROVAL,
    )

    report.reporter = citizen
    report.category = category
    report.followers = []
    report.created_at = datetime.utcnow()

    return report


@pytest.fixture
def photo():
    p = MagicMock()
    p.filename = "photo.jpg"
    p.content_type = "image/jpeg"
    return p


# -------------------------
# get_report
# -------------------------

def test_get_report_not_found(make_service):
    service = make_service()

    service.report_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_report(1)


# -------------------------
# get_accessible_report
# -------------------------

@pytest.mark.parametrize(
    ("role", "category_id", "allowed"),
    [
        (Role.ADMIN, None, True),
        (Role.OPERATOR, 10, True),
        (Role.OPERATOR, 999, False),
        (Role.CITIZEN, None, False),
    ],
)
def test_get_accessible_report_permissions(
    make_service,
    report,
    role,
    category_id,
    allowed,
):
    service = make_service()

    user = User(
        id=50,
        username="user",
        role=role,
        category_id=category_id,
    )

    service.report_repository.get_by_id.return_value = report

    if allowed:
        assert service.get_accessible_report(99, user) == report
    else:
        with pytest.raises(AuthorizationError):
            service.get_accessible_report(99, user)

    user_none = None

    with pytest.raises(AuthorizationError):
        service.get_accessible_report(99, user_none)


# -------------------------
# create_report
# -------------------------

@pytest.mark.parametrize(
    ("payload", "error"),
    [
        (
            {"category_id": "x"},
            "A valid active category is required.",
        ),
        (
            {"title": ""},
            "Title and description are required.",
        ),
        (
            {"latitude": "bad"},
            "Latitude and longitude must be valid numbers.",
        ),
        (
            {"photos": []},
            "At least one photo is required.",
        ),
    ],
)
def test_create_report_validation(
    make_service,
    citizen,
    category,
    photo,
    payload,
    error,
):
    service = make_service()

    service.category_repository.get_by_id.return_value = category

    params = {
        "reporter": citizen,
        "category_id": 10,
        "title": "Title",
        "description": "Description",
        "latitude": 45.0,
        "longitude": 9.0,
        "photos": [photo],
    }

    params.update(payload)

    with pytest.raises(ValidationError, match=error):
        service.create_report(**params)


def test_create_report_success(make_service, citizen, category, photo):
    service = make_service()

    service.category_repository.get_by_id.return_value = category
    service.storage_service.save.return_value = "uploads/photo.jpg"

    created_report = Report(id=123)

    service.report_repository.get_by_id.return_value = created_report

    def assign_id(report):
        report.id = 123

    service.report_repository.add.side_effect = assign_id

    result = service.create_report(
        reporter=citizen,
        category_id=10,
        title=" Title ",
        description=" Description ",
        latitude="45.0",
        longitude="9.0",
        photos=[photo],
    )

    assert result == created_report

    service.report_repository.add_photo.assert_called_once()
    service.report_repository.add_status_entry.assert_called_once()

    service.session.commit.assert_called_once()



def test_create_report_too_many_photos(make_service, citizen, category, photo):
    service = make_service()
    service.category_repository.get_by_id.return_value = category
    with pytest.raises(ValidationError, match="at most 3 photos"):
        service.create_report(
            reporter=citizen, category_id=10, title="T", description="D",
            latitude=45, longitude=9,
            photos=[photo, photo, photo, photo] # 4 foto per far scattare l'if
        )
# -------------------------
# follow_report
# -------------------------

def test_follow_report_requires_public(make_service, report, citizen):
    service = make_service()

    service.report_repository.get_by_id.return_value = report

    with pytest.raises(ValidationError):
        service.follow_report(99, citizen)


def test_follow_report_already_following(make_service, report, citizen):
    service = make_service()
    report.status = ReportStatus.ASSIGNED
    service.report_repository.get_by_id.return_value = report
    # Simuliamo che il repository trovi già un follower
    service.report_repository.get_follower.return_value = MagicMock()

    res = service.follow_report(99, citizen)
    # Deve restituire il report senza chiamare add_follower
    assert res == report
    assert service.report_repository.add_follower.called is False
# -------------------------
# assign_report
# -------------------------

def test_assign_report(make_service, report, operator, citizen):
    service = make_service()

    service.report_repository.get_by_id.return_value = report

    result = service.assign_report(99, operator)

    assert result.status == ReportStatus.ASSIGNED

    service.notification_service.notify_status_change.assert_called_once()
    service.session.commit.assert_called_once()

    with pytest.raises(AuthorizationError):
        service.assign_report(99, citizen)


# -------------------------
# update_status
# -------------------------

@patch("participium.services.report_service.ensure_transition_allowed")
def test_update_status(
    mock_transition,
    make_service,
    report,
    operator,
    citizen
):
    service = make_service()

    service.report_repository.get_by_id.return_value = report

    updated = service.update_status(
        report_id=99,
        operator=operator,
        next_status_value=ReportStatus.IN_PROGRESS.value,
        note="Started",
    )

    assert updated.status == ReportStatus.IN_PROGRESS

    mock_transition.assert_called_once()

    service.notification_service.notify_status_change.assert_called_once()

    service.session.commit.assert_called_once()

    with pytest.raises(AuthorizationError):
        service.update_status(
            report_id=99,
            operator=citizen,
            next_status_value=ReportStatus.IN_PROGRESS.value,
            note="Started")


def test_update_status_invalid_status(make_service, report, operator):
    service = make_service()

    service.report_repository.get_by_id.return_value = report

    with pytest.raises(ValidationError):
        service.update_status(
            report_id=99,
            operator=operator,
            next_status_value="INVALID",
        )

def test_update_status_rejection_needs_note(make_service, report, operator):
    service = make_service()
    service.report_repository.get_by_id.return_value = report

    with pytest.raises(ValidationError, match="Rejection reason is required."):
        service.update_status(
            report_id=99,
            operator=operator,
            next_status_value=ReportStatus.REJECTED.value,
            note=None  # Questo scatena l'errore
        )
# -------------------------
# export_rows
# -------------------------

def test_export_rows(make_service, report, category):
    service = make_service()

    report.status = ReportStatus.ASSIGNED
    report.category = category

    service.report_repository.list_reports.return_value = [report]

    rows = service.export_rows()

    assert rows[0]["id"] == report.id
    assert rows[0]["category"] == category.name


# -------------------------
# static helpers
# -------------------------

def test_is_public(report):
    report.status = ReportStatus.ASSIGNED

    assert ReportService.is_public(report) is True


def test_ensure_operator_category_access(report, citizen, operator, admin):
    assert ReportService._ensure_operator_category_access(admin, report) is None

    with pytest.raises(AuthorizationError):
        ReportService._ensure_operator_category_access(citizen, report)

    op = operator
    op.category_id = 15

    with pytest.raises(AuthorizationError):
        ReportService._ensure_operator_category_access(op, report)

# -------------------------
# list_reports
# -------------------------

def test_list_public_reports(make_service):
    service = make_service()
    service.list_public_reports(category_id=10)
    service.report_repository.list_reports.assert_called_once_with(
        public_only=True,
        category_id=10,
        status=None,
        date_from=None,
        date_to=None,
        sort="desc"
    )

def test_list_user_reports(make_service, citizen):
    service = make_service()
    service.list_user_reports(citizen)
    service.report_repository.list_user_reports.assert_called_once_with(citizen.id)


def test_list_public_reports_full_filters(make_service):
    service = make_service()
    now = datetime.utcnow()
    service.list_public_reports(
        category_id=1, status=ReportStatus.ASSIGNED,
        date_from=now, date_to=now, sort="asc"
    )
    service.report_repository.list_reports.assert_called_once_with(
        public_only=True, category_id=1, status=ReportStatus.ASSIGNED,
        date_from=now, date_to=now, sort="asc"
    )


def test_list_specialized_reports(make_service, operator):
    service = make_service()


    service.list_pending_reports({"category_id": 1})
    service.report_repository.list_pending.assert_called_once()


    service.list_operator_reports(operator)
    service.report_repository.list_operator_reports.assert_called_once_with(
        operator.role, operator.category_id
    )
# -------------------------
# unfollow_report
# -------------------------

def test_unfollow_report_success(make_service, report, citizen):
    service = make_service()
    follower_mock = MagicMock()
    service.report_repository.get_by_id.return_value = report
    service.report_repository.get_follower.return_value = follower_mock

    service.unfollow_report(99, citizen)

    service.report_repository.remove_follower.assert_called_once_with(follower_mock)
    service.session.commit.assert_called_once()




# -------------------------
# _recipients
# -------------------------

def test_recipients_logic(report, citizen):
    follower_user = User(id=55, username="follower")
    follower_obj = MagicMock()
    follower_obj.user = follower_user
    report.followers = [follower_obj]


    recipients = ReportService._recipients(report)

    assert citizen in recipients
    assert follower_user in recipients
    assert len(recipients) == 2

# -------------------------
# assign_report
# -------------------------
def test_assign_report_invalid_status(make_service, report, operator):
    service = make_service()
    report.status = ReportStatus.IN_PROGRESS  # Non è PENDING_APPROVAL
    service.report_repository.get_by_id.return_value = report

    with pytest.raises(ValidationError, match="Only pending reports can be assigned"):
        service.assign_report(99, operator)