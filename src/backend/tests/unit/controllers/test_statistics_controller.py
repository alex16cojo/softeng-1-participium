import pytest
from unittest.mock import Mock

from participium.controllers.statistics_controller import StatisticsController


@pytest.fixture
def controller_bundle():
    statistics_service = Mock()

    controller = StatisticsController(statistics_service=statistics_service)

    return {
        "controller": controller,
        "statistics_service": statistics_service,
    }


@pytest.mark.unit
def test_public_statistics_default(controller_bundle):
    controller = controller_bundle["controller"]
    statistics_service = controller_bundle["statistics_service"]

    stats = {
        "total_reports": 150
    }
    statistics_service.public_statistics.return_value = stats

    result = controller.public_statistics()

    statistics_service.public_statistics.assert_called_once_with("day")
    assert result == stats


@pytest.mark.unit
def test_public_statistics_custom_granularity(controller_bundle):
    controller = controller_bundle["controller"]
    statistics_service = controller_bundle["statistics_service"]

    stats = {
        "total_reports": 500
    }
    granularity = "month"
    statistics_service.public_statistics.return_value = stats

    result = controller.public_statistics(granularity)

    statistics_service.public_statistics.assert_called_once_with(granularity)
    assert result == stats