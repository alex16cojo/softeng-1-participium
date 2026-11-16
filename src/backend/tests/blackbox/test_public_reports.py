from __future__ import annotations
from dataclasses import field
from datetime import datetime

import pytest

from participium.models.enums import ReportStatus
from participium.models.report import Report
from participium.services.report_service import ReportService

REPORT_BASE = Report(
    id=1,
    title="", description="", latitude=0.0, longitude=0.0,
    is_anonymous=False, status=ReportStatus.PENDING_APPROVAL,
    rejection_reason=None, reporter_id=None, category_id=1,
    reporter=None, category=None,
    photos=[],
    followers=[],
    created_at=datetime(2025, 3, 21)
)

REPORT_ID_2 = Report(
    id=2,
    title="", description="", latitude=0.0, longitude=0.0,
    is_anonymous=False, status=ReportStatus.PENDING_APPROVAL,
    rejection_reason=None, reporter_id=None, category_id=2,
    reporter=None, category=None,
    photos=[],
    followers=[],
    created_at=datetime(2025, 3, 21)
)

REPORT_STATUS_ASSIGNED = Report(
    id=3,
    title="", description="", latitude=0.0, longitude=0.0,
    is_anonymous=False, status=ReportStatus.ASSIGNED,
    rejection_reason=None, reporter_id=None, category_id=1,
    reporter=None, category=None,
    photos=[],
    followers=[],
    created_at=datetime(2025, 3, 21)
)

REPORT_DATE_FROM_2017 = Report(
    id=4,
    title="", description="", latitude=0.0, longitude=0.0,
    is_anonymous=False, status=ReportStatus.PENDING_APPROVAL,
    rejection_reason=None, reporter_id=None, category_id=1,
    reporter=None, category=None,
    photos=[],
    followers=[],
    created_at=datetime(2017, 5, 15)
)

REPORT_DATE_TO_2027 = Report(
    id=5,
    title="", description="", latitude=0.0, longitude=0.0,
    is_anonymous=False, status=ReportStatus.PENDING_APPROVAL,
    rejection_reason=None, reporter_id=None, category_id=1,
    reporter=None, category=None,
    photos=[],
    followers=[],
    created_at=datetime(2027, 8, 11)
)

ALL_ASC = [REPORT_DATE_FROM_2017, REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED, REPORT_DATE_TO_2027]
ALL_DESC = list(reversed(ALL_ASC))


@pytest.mark.skip(reason="Disabled.")
@pytest.mark.parametrize("category_id, status, date_from, date_to, sort, expected", [
    (
        -1, ReportStatus.PENDING_APPROVAL,
        datetime(2025, 3, 21), datetime(2026, 2, 15),
        "asc",
        []
    ),
    (
        None, None, None, None,
        "asc",
        ALL_ASC
    ),
    (
        2, None, None, None,
        "asc",
        [REPORT_ID_2]
    ),
    (
        1, ReportStatus.ASSIGNED, None, None,
        "asc",
        [REPORT_STATUS_ASSIGNED]
    ),
    (
        None, None, None, None,
        "desc",
        ALL_DESC
    ),
    (
        None, None, None, None,
        "",
        ALL_DESC
    ),
    (
        None, ReportStatus.PENDING_APPROVAL,
        datetime(2025, 3, 21), datetime(2026, 2, 15),
        "asc",
        [REPORT_BASE, REPORT_ID_2]
    ),
    (
        1, ReportStatus.PENDING_APPROVAL,
        None, datetime(2026, 2, 15),
        "asc",
        [REPORT_DATE_FROM_2017, REPORT_BASE]
    ),
    (
        1, ReportStatus.PENDING_APPROVAL,
        datetime(2025, 3, 21), None,
        "asc",
        [REPORT_BASE, REPORT_DATE_TO_2027]
    ),
    (
        1, ReportStatus.PENDING_APPROVAL,
        datetime(2025, 3, 21), datetime(2020, 2, 15),
        "asc",
        []
    ),
    (
        1, ReportStatus.PENDING_APPROVAL,
        datetime(2015, 3, 21), datetime(2016, 5, 15),
        "asc",
        []
    ),
    (
        1, ReportStatus.PENDING_APPROVAL,
        datetime(2025, 3, 21), datetime(2025, 3, 21),
        "asc",
        [REPORT_BASE]
    ),
    (
        None, None,
        datetime(2025, 3, 21), datetime(2026, 2, 15),
        "asc",
        [REPORT_BASE, REPORT_ID_2, REPORT_STATUS_ASSIGNED]
    ),
    (
        None, None,
        datetime(2025, 3, 21), datetime(2026, 2, 15),
        "desc",
        [REPORT_STATUS_ASSIGNED, REPORT_ID_2, REPORT_BASE]
    ),
])
def test_list_public_reports(category_id, status, date_from, date_to, sort, expected) -> None:
    report_service = ReportService()
    assert report_service.list_public_reports(category_id, status, date_from, date_to, sort) == expected
