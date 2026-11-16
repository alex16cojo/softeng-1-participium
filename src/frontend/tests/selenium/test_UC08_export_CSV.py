import pytest
import time

from tests.conftest import (
    BASE_URL,
    driver,
    wait,
    wait_for,
    finds,
    ensure_logged_out
)


class TestExportReports:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        driver.get(f"{BASE_URL}")
        ensure_logged_out(driver, wait)

        wait_for(wait, "public-report-table-body")

    def test_export_reports_with_data(self, driver, wait):
        export_link = wait_for(wait, "public-export-link")
        assert export_link.is_displayed()

        export_link.click()
        time.sleep(1)

        driver.switch_to.window(driver.window_handles[0])

    @pytest.mark.implementation_bug(reason="BUG-UC08 - Export link remains active even when the report list is empty, allowing empty CSV downloads")
    def test_empty_reports_list_hides_export_link(self, driver, wait):
        date_from_input = wait_for(wait, "public-filter-date-from")
        date_from_input.send_keys("01/01/2099\t12:00")

        wait_for(wait, "public-filter-submit").click()
        time.sleep(1)

        export_links = finds(driver, "public-export-link")
        assert len(export_links) == 0