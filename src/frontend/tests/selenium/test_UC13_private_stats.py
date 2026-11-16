import pytest
from selenium.webdriver.common.by import By

from tests.conftest import (
    BASE_URL,
    ADMIN_USER,
    ADMIN_PASSWORD,
    driver,
    wait,
    wait_for,
    ensure_logged_out,
    login,
    finds
)


class TestPrivateStatistics:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        driver.get(f"{BASE_URL}")
        ensure_logged_out(driver, wait)

        login(driver, wait, ADMIN_USER, ADMIN_PASSWORD)
        wait_for(wait, "admin-statistics-section")

    def test_admin_can_view_private_statistics(self, driver, wait):
        wait_for(wait, "admin-stats-grid")

        expected_metrics_ids = [
            "admin-metric-item-reports-by-status",
            "admin-metric-item-reports-by-type",
            "admin-metric-item-reports-by-reporter",
            "admin-metric-item-top-1-percent-by-type",
            "admin-metric-item-top-5-percent-by-type"
        ]

        for metric_id in expected_metrics_ids:

            metric_container = wait_for(wait, metric_id)
            assert metric_container.is_displayed()

    @pytest.mark.implementation_bug(
        reason="BUG-UC13: Public statistics are missing from the admin dashboard. The scenario requires both public and private statistics.")
    def test_admin_dashboard_includes_public_statistics(self, driver, wait):
        public_stats = finds(driver, "public-statistics-card")
        assert len(public_stats) > 0

    @pytest.mark.implementation_bug(
        reason="BUG-UC13: System renders only plain text lists without any graphical chart.")
    def test_statistics_rendered_as_charts(self, driver, wait):
        stats_grid = wait_for(wait, "admin-stats-grid")

        charts = stats_grid.find_elements(By.CSS_SELECTOR, "canvas, svg")
        assert len(charts) > 0