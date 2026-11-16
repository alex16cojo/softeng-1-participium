from __future__ import annotations

from unittest.mock import Mock
import pytest

from participium.models.report import Report, ReportStatus
from participium.models.category import Category
from participium.services.report_service import ReportService
from participium.core.exceptions import ValidationError

pytestmark = pytest.mark.whitebox


def _report(*, id: int, title: str, reporter_id: int) -> Report:
    return Report(
        id=id,
        title=title.strip(),
        description="Descrizione valida",
        latitude=45.0,
        longitude=9.0,
        reporter_id=reporter_id,
        category_id=10,
        status=ReportStatus.PENDING_APPROVAL
    )


def _category(*, id: int, is_active: bool = True) -> Category:
    cat = Mock(spec=Category)
    cat.id = id
    cat.is_active = is_active
    return cat


@pytest.fixture
def report_service_bundle() -> dict[str, object]:
    session = Mock()
    report_repo = Mock()
    cat_repo = Mock()
    storage = Mock()

    service = ReportService(
        session=session,
        report_repository=report_repo,
        category_repository=cat_repo,
        storage_service=storage,
    )

    service.get_report = Mock()

    return {
        "service": service,
        "session": session,
        "report_repo": report_repo,
        "cat_repo": cat_repo,
        "storage": storage,
        "reporter": Mock(id=1),
    }


@pytest.fixture
def valid_category_case(report_service_bundle: dict[str, object]) -> dict[str, object]:
    category = _category(id=10, is_active=True)
    report_service_bundle["cat_repo"].get_by_id.return_value = category
    return report_service_bundle


@pytest.fixture
def inactive_category_case(report_service_bundle: dict[str, object]) -> dict[str, object]:
    category = _category(id=10, is_active=False)
    report_service_bundle["cat_repo"].get_by_id.return_value = category
    return report_service_bundle


# P1
def test_malformed_category_id(report_service_bundle: dict[str, object]) -> None:
    service = report_service_bundle["service"]
    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(reporter=report_service_bundle["reporter"], category_id="abc", title="T",
                              description="D", latitude=1.0, longitude=1.0, photos=[Mock()])


# P2
def test_none_category_id(report_service_bundle: dict[str, object]) -> None:
    service = report_service_bundle["service"]
    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(reporter=report_service_bundle["reporter"], category_id=None, title="T",
                              description="D", latitude=1.0, longitude=1.0, photos=[Mock()])


# P3
def test_unknown_category(report_service_bundle: dict[str, object]) -> None:
    service = report_service_bundle["service"]
    report_service_bundle["cat_repo"].get_by_id.return_value = None
    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(reporter=report_service_bundle["reporter"], category_id=-1, title="T",
                              description="D", latitude=1.0, longitude=1.0, photos=[Mock()])


# P4
def test_inactive_category(inactive_category_case: dict[str, object]) -> None:
    service = inactive_category_case["service"]
    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(reporter=inactive_category_case["reporter"], category_id=10, title="T",
                              description="D", latitude=1.0, longitude=1.0, photos=[Mock()])


# P5
def test_missing_title(valid_category_case: dict[str, object]) -> None:
    service = valid_category_case["service"]
    with pytest.raises(ValidationError, match="Title and description are required."):
        service.create_report(reporter=valid_category_case["reporter"], category_id=10, title=None,
                              description="Desc", latitude=1.0, longitude=1.0, photos=[Mock()])


# P6
def test_missing_description(valid_category_case: dict[str, object]) -> None:
    service = valid_category_case["service"]
    with pytest.raises(ValidationError, match="Title and description are required."):
        service.create_report(reporter=valid_category_case["reporter"], category_id=10, title="Titolo",
                              description=None, latitude=1.0, longitude=1.0, photos=[Mock()])


# P7
def test_missing_latitude(valid_category_case: dict[str, object]) -> None:
    service = valid_category_case["service"]
    with pytest.raises(ValidationError, match="Latitude and longitude are required."):
        service.create_report(reporter=valid_category_case["reporter"], category_id=10, title="T",
                              description="D", latitude=None, longitude=1.0, photos=[Mock()])


# P8
def test_missing_longitude(valid_category_case: dict[str, object]) -> None:
    service = valid_category_case["service"]
    with pytest.raises(ValidationError, match="Latitude and longitude are required."):
        service.create_report(reporter=valid_category_case["reporter"], category_id=10, title="T",
                              description="D", latitude=1.0, longitude=None, photos=[Mock()])


# P9
def test_invalid_coordinate_format(valid_category_case: dict[str, object]) -> None:
    service = valid_category_case["service"]
    with pytest.raises(ValidationError, match="Latitude and longitude must be valid numbers."):
        service.create_report(reporter=valid_category_case["reporter"], category_id=10, title="T",
                              description="D", latitude="error", longitude=1.0, photos=[Mock()])


# P10
def test_zero_valid_photos(valid_category_case: dict[str, object]) -> None:
    service = valid_category_case["service"]
    invalid_photo = Mock(filename=None)
    with pytest.raises(ValidationError, match="At least one photo is required."):
        service.create_report(reporter=valid_category_case["reporter"], category_id=10, title="T",
                              description="D", latitude=1.0, longitude=1.0, photos=[invalid_photo])


# P11
def test_more_than_three_photos(valid_category_case: dict[str, object]) -> None:
    service = valid_category_case["service"]
    photos = [Mock(filename=f"foto{i}.jpg") for i in range(4)]
    with pytest.raises(ValidationError, match="at most 3 photos"):
        service.create_report(reporter=valid_category_case["reporter"], category_id=10, title="T",
                              description="D", latitude=1.0, longitude=1.0, photos=photos)


# P12 - P13 - P14
@pytest.mark.parametrize("num_photos", [1, 2, 3])
def test_create_report_success(valid_category_case: dict[str, object], num_photos: int) -> None:
    service = valid_category_case["service"]
    report_repo = valid_category_case["report_repo"]
    storage = valid_category_case["storage"]
    session = valid_category_case["session"]
    reporter = valid_category_case["reporter"]

    photos = [Mock(filename=f"foto{i}.jpg", content_type="image/jpeg") for i in range(num_photos)]
    storage.save.return_value = f"/path/to/img.jpg"

    expected_report = _report(id=100, title="Semaforo", reporter_id=reporter.id)
    service.get_report.return_value = expected_report

    result = service.create_report(
        reporter=reporter,
        category_id=10,
        title="Semaforo",
        description="Descrizione",
        latitude=45.0,
        longitude=9.0,
        photos=photos
    )


    assert result == expected_report
    report_repo.add.assert_called_once()
    assert storage.save.call_count == num_photos
    assert report_repo.add_photo.call_count == num_photos
    report_repo.add_status_entry.assert_called_once()
    session.commit.assert_called_once()
