import pytest
import time
from selenium.webdriver.common.by import By

from tests.conftest import (
    BASE_URL,
    driver,
    wait,
    wait_for,
    find,
    ensure_logged_out
)


class TestPublicStatistics:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        driver.get(f"{BASE_URL}")
        ensure_logged_out(driver, wait)

        wait_for(wait, "public-statistics-card")

    def test_granularity_selection_updates_trends(self, driver, wait):
        granularity_select = wait_for(wait, "public-stat-granularity")

        # salvo lo stato iniziale
        initial_trend_text = wait_for(wait, "public-trend-statistics").text

        # modifico la granularità
        granularity_select.send_keys("Month")
        wait_for(wait, "public-filter-submit").click()
        time.sleep(1)

        updated_trend_text = wait_for(wait, "public-trend-statistics").text

        assert initial_trend_text != updated_trend_text

    @pytest.mark.implementation_bug(reason="BUG-UC09: System renders only plain text lists without any graphical chart for category and trend statistics.")
    def test_statistics_rendered_as_charts(self, driver, wait):
        stats_grid = wait_for(wait, "public-statistics-grid")

        charts = stats_grid.find_elements(By.CSS_SELECTOR, "canvas, svg")
        assert len(charts) > 0

    @pytest.mark.implementation_bug(reason="BUG-UC09: When no data is available, no error message is shown.")
    def test_empty_statistics_display_error_message(self, driver, wait):
        date_from_input = wait_for(wait, "public-filter-date-from")
        date_from_input.send_keys("01/01/2099\t12:00")

        wait_for(wait, "public-filter-submit").click()
        time.sleep(1)

        error_message = find(driver, "public-statistics-error")

        assert error_message.is_displayed()