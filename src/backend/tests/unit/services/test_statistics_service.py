from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from participium.models.enums import ReportStatus
from participium.services.statistics_service import StatisticsService


# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def service():
    repository = MagicMock()

    return StatisticsService(repository)


@pytest.fixture
def reports():
    def make_report(
        *,
        reporter_id,
        username,
        category,
        status,
        created_at,
    ):
        reporter = None

        if reporter_id is not None:
            reporter = MagicMock()
            reporter.id = reporter_id
            reporter.username = username

        category_obj = MagicMock()
        category_obj.name = category

        status_obj = MagicMock()
        status_obj.value = status

        report = MagicMock()

        report.reporter = reporter
        report.category = category_obj
        report.status = status_obj
        report.created_at = created_at

        return report

    return [
        make_report(
            reporter_id=1,
            username="mario",
            category="Roads",
            status=ReportStatus.ASSIGNED.value,
            created_at=datetime(2026, 1, 10),
        ),
        make_report(
            reporter_id=1,
            username="mario",
            category="Roads",
            status=ReportStatus.IN_PROGRESS.value,
            created_at=datetime(2026, 1, 11),
        ),
        make_report(
            reporter_id=2,
            username="luigi",
            category="Lighting",
            status=ReportStatus.ASSIGNED.value,
            created_at=datetime(2026, 1, 11),
        ),
    ]


# -------------------------
# public_statistics
# -------------------------

def test_public_statistics(service, reports):
    service.report_repository.list_reports.return_value = reports

    result = service.public_statistics()

    assert result["total_reports"] == 3

    assert result["reports_by_category"] == {
        "Roads": 2,
        "Lighting": 1,
    }

    assert result["trends"] == {
        "2026-01-10": 1,
        "2026-01-11": 2,
    }

    service.report_repository.list_reports.assert_called_once_with(public_only=True)


# -------------------------
# admin_statistics
# -------------------------

def test_admin_statistics(service, reports):
    service.report_repository.list_all.return_value = reports

    result = service.admin_statistics()

    assert result["reports_by_status"] == {
        ReportStatus.ASSIGNED.value: 2,
        ReportStatus.IN_PROGRESS.value: 1,
    }

    assert result["reports_by_type"] == {
        "Roads": 2,
        "Lighting": 1,
    }

    assert "top_1_percent_by_type" in result
    assert "top_5_percent_by_type" in result


# -------------------------
# _aggregate_trends
# -------------------------

@pytest.mark.parametrize(
    ("granularity", "expected"),
    [
        (
            "day",
            {
                "2026-01-10": 1,
                "2026-01-11": 2,
            },
        ),
        (
            "month",
            {
                "2026-01": 3,
            },
        ),
        (
            "week",
            {
                "2026-W02": 3,
            },
        ),
    ],
)
def test_aggregate_trends(service, reports, granularity, expected):
    result = service._aggregate_trends(reports, granularity)

    assert result == expected


# -------------------------
# _top_percent_breakdown
# -------------------------

def test_top_percent_breakdown(service, reports):
    result = service._top_percent_breakdown(reports, 1)

    assert result == {
        "Roads": 2,
    }


def test_top_percent_breakdown_empty(service):
    result = service._top_percent_breakdown([], 1)

    assert result == {}


# -------------------------
# _reporter_label
# -------------------------

def test_reporter_label():
    reporter = MagicMock()
    reporter.id = 1
    reporter.username = "mario"

    report = MagicMock()
    report.reporter = reporter

    result = StatisticsService._reporter_label(report)

    assert result == "mario (1)"


def test_reporter_label_deleted_user():
    report = MagicMock()
    report.reporter = None

    result = StatisticsService._reporter_label(report)

    assert result == "Deleted Citizen"


def test_public_statistics_with_granularities(service, reports):
    """Test public_statistics with all granularities."""
    service.report_repository.list_reports.return_value = reports

    result = service.public_statistics(granularity="day")
    assert "2026-01-10" in result["trends"]

    result = service.public_statistics(granularity="month")
    assert "2026-01" in result["trends"]

    result = service.public_statistics(granularity="week")
    assert "2026-W02" in result["trends"]


def test_public_statistics_empty_reports(service):
    """Test public_statistics with no reports."""
    service.report_repository.list_reports.return_value = []

    result = service.public_statistics()

    assert result["total_reports"] == 0
    assert result["reports_by_category"] == {}
    assert result["trends"] == {}


def test_admin_statistics_all_breakdowns(service, reports):
    """Test that admin_statistics includes all required breakdowns."""
    service.report_repository.list_all.return_value = reports

    result = service.admin_statistics()

    required_keys = [
        "reports_by_status",
        "reports_by_type",
        "reports_by_type_and_status",
        "reports_by_reporter",
        "reports_by_reporter_and_type",
        "reports_by_reporter_type_and_status",
        "top_1_percent_by_type",
        "top_5_percent_by_type",
    ]

    for key in required_keys:
        assert key in result


def test_admin_statistics_type_and_status(service, reports):
    """Test admin_statistics type and status breakdown."""
    service.report_repository.list_all.return_value = reports

    result = service.admin_statistics()

    assert "Roads | Assigned" in result["reports_by_type_and_status"]
    assert "Roads | In Progress" in result["reports_by_type_and_status"]
    assert "Lighting | Assigned" in result["reports_by_type_and_status"]


def test_admin_statistics_reporter_breakdown(service, reports):
    """Test admin_statistics reporter breakdown."""
    service.report_repository.list_all.return_value = reports

    result = service.admin_statistics()

    assert "mario (1)" in result["reports_by_reporter"]
    assert "luigi (2)" in result["reports_by_reporter"]
    assert result["reports_by_reporter"]["mario (1)"] == 2
    assert result["reports_by_reporter"]["luigi (2)"] == 1


def test_admin_statistics_reporter_and_type(service, reports):
    """Test admin_statistics reporter and type breakdown."""
    service.report_repository.list_all.return_value = reports

    result = service.admin_statistics()

    assert "mario (1) | Roads" in result["reports_by_reporter_and_type"]
    assert "luigi (2) | Lighting" in result["reports_by_reporter_and_type"]


def test_admin_statistics_reporter_type_status(service, reports):
    """Test admin_statistics reporter, type, and status breakdown."""
    service.report_repository.list_all.return_value = reports

    result = service.admin_statistics()

    assert "mario (1) | Roads | Assigned" in result["reports_by_reporter_type_and_status"]
    assert "mario (1) | Roads | In Progress" in result["reports_by_reporter_type_and_status"]


def test_top_percent_breakdown_1_percent(service, reports):
    """Test top 1% breakdown with multiple reporters."""
    result = service._top_percent_breakdown(reports, 1)

    assert "Roads" in result
    assert result["Roads"] == 2


def test_top_percent_breakdown_5_percent(service, reports):
    """Test top 5% breakdown with multiple reporters."""
    result = service._top_percent_breakdown(reports, 5)

    assert isinstance(result, dict)
    assert len(result) > 0


def test_top_percent_breakdown_100_percent(service, reports):
    """Test top 100% breakdown includes all reporters."""
    result = service._top_percent_breakdown(reports, 100)

    assert "Roads" in result
    assert "Lighting" in result
    assert result["Roads"] == 2
    assert result["Lighting"] == 1


def test_aggregate_trends_sorted_output(service):
    """Test that trends are sorted by date."""
    reports_out_of_order = []
    
    for day in [20, 15, 18]:
        report = MagicMock()
        report.created_at = datetime(2026, 1, day)
        reports_out_of_order.append(report)

    result = service._aggregate_trends(reports_out_of_order, "day")
    keys = list(result.keys())

    assert keys == ["2026-01-15", "2026-01-18", "2026-01-20"]


def test_aggregate_trends_empty(service):
    """Test aggregate_trends with empty reports."""
    result = service._aggregate_trends([], "day")

    assert result == {}


def test_admin_statistics_deleted_reporter(service):
    """Test admin_statistics with deleted reporter."""
    report_with_deleted = MagicMock()
    report_with_deleted.reporter = None
    report_with_deleted.category = MagicMock(name="Roads")
    report_with_deleted.status = MagicMock(value=ReportStatus.ASSIGNED.value)

    service.report_repository.list_all.return_value = [report_with_deleted]

    result = service.admin_statistics()

    assert "Deleted Citizen" in result["reports_by_reporter"]
    assert result["reports_by_reporter"]["Deleted Citizen"] == 1


def test_admin_statistics_empty_reports(service):
    """Test admin_statistics with no reports."""
    service.report_repository.list_all.return_value = []

    result = service.admin_statistics()

    assert result["reports_by_status"] == {}
    assert result["reports_by_type"] == {}
    assert result["reports_by_reporter"] == {}
    assert result["top_1_percent_by_type"] == {}
    assert result["top_5_percent_by_type"] == {}