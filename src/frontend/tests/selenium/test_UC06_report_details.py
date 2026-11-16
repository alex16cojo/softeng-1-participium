import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.conftest import (
    BASE_URL,
    driver,
    wait,
    ensure_logged_out,
    wait_for
)


class TestViewReportDetails:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        driver.get(f"{BASE_URL}")
        ensure_logged_out(driver, wait)

        wait_for(wait,"public-report-table-body")

        open_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#public-report-table-body tr a[id$='-open-link']")))
        open_link.click()

        wait_for(wait, "report-detail-page")

    def test_report_details(self, driver, wait):
        assert wait_for(wait, "report-detail-title").is_displayed()
        assert wait_for(wait, "report-detail-description").is_displayed()
        assert wait_for(wait, "report-detail-category").is_displayed()
        assert wait_for(wait, "report-detail-status").is_displayed()
        assert wait_for(wait, "status-history-card").is_displayed()
        assert wait_for(wait, "report-detail-map-card").is_displayed()
        assert wait_for(wait, "report-detail-photo-grid").is_displayed()


class TestReportNotFound:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        ensure_logged_out(driver, wait)

    def test_report_unavailable_displays_error(self, driver, wait):
        driver.get(f"{BASE_URL}/reports/999999")
        wait_for(wait, "report-detail-page")
        error_message = wait_for(wait, "report-detail-error")

        assert error_message.is_displayed()