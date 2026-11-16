import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from tests.conftest import (
    driver,
    wait,
    login,
    logout,
    OPERATOR_USER,
    OPERATOR_PASSWORD,
)


class TestManageReport:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        login(driver, wait, OPERATOR_USER, OPERATOR_PASSWORD)
        yield
        logout(driver, wait)

    def test_operator_sees_pending_reports(self, driver):
        pending_table = driver.find_element(
            By.ID,
            "pending-reports-table"
        )
        assert pending_table.is_displayed()
        rows = driver.find_elements(
            By.CSS_SELECTOR,
            "#pending-reports-table-body tr"
        )
        assert len(rows) > 0

    def test_operator_sees_assigned_reports(self, driver):
        assigned_table = driver.find_element(
            By.ID,
            "assigned-reports-table"
        )
        assert assigned_table.is_displayed()

        rows = driver.find_elements(
            By.CSS_SELECTOR,
            "#assigned-reports-table-body tr"
        )
        assert len(rows) > 0

    def test_operator_can_assign_report(self, driver):

        assign_button = driver.find_element(
            By.ID,
            "pending-report-assign-1"
        )
        assert assign_button.is_displayed()

        assign_button.click()

        assigned_table = driver.find_element(
            By.ID,
            "assigned-reports-table"
        )
        assert assigned_table.is_displayed()

    def test_operator_can_open_report_detail(self, driver):

        detail_link = driver.find_element(
            By.ID,
            "assigned-report-row-2-open-detail"
        )
        href = detail_link.get_attribute("href")
        assert href is not None
        assert "/reports/" in href

    def test_operator_can_change_status(self, driver):
        status_select = Select(
            driver.find_element(
                By.ID,
                "assigned-report-status-2"
            )
        )
        status_select.select_by_visible_text(
            "In Progress"
        )
        driver.find_element(
            By.ID,
            "assigned-report-update-2"
        ).click()

        selected_status = Select(
            driver.find_element(
                By.ID,
                "assigned-report-status-2"
            )
        ).first_selected_option.text
        assert selected_status == "In Progress"

    def test_operator_can_add_note(self, driver):

        note_field = driver.find_element(
            By.ID,
            "assigned-report-note-2"
        )

        note_field.clear()

        note_field.send_keys(
            "Work scheduled for next week"
        )

        driver.find_element(
            By.ID,
            "assigned-report-update-2"
        ).click()

        saved_note = driver.find_element(
            By.ID,
            "assigned-report-note-2"
        ).get_attribute("value")

        assert saved_note == "Work scheduled for next week"

    def test_rejected_status_requires_reason(self, driver):

        status_select = Select(
            driver.find_element(
                By.ID,
                "assigned-report-status-2"
            )
        )

        status_select.select_by_visible_text(
            "Rejected"
        )

        note_field = driver.find_element(
            By.ID,
            "assigned-report-note-2"
        )

        note_field.clear()

        driver.find_element(
            By.ID,
            "assigned-report-update-2"
        ).click()

        error = driver.find_element(
            By.ID,
            "operator-error"
        )
        assert error.is_displayed()
        assert (
            error.text
            == "Rejection reason is required."
        )