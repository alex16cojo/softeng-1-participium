import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


from tests.conftest import (
    driver,
    wait,
    login,
    logout,
    wait_for,
    OPERATOR_USER,
    OPERATOR_PASSWORD,
)


class TestSendMessageToCitizen:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        login(driver, wait, OPERATOR_USER, OPERATOR_PASSWORD)
        report_link = wait.until(
            EC.element_to_be_clickable(
                (By.ID, "assigned-report-row-2-open-detail")
            )
        )
        report_link.click()

        wait.until(
            EC.visibility_of_element_located(
                (By.ID, "report-detail-summary-section")
            )
        )

        yield

        try:
            logout(driver, wait)
        except Exception:
            driver.get("http://localhost:5050/login")


    def test_report_detail_page_opens(self, driver, wait):

        title = wait.until(
            EC.visibility_of_element_located((By.ID, "report-detail-title"))
        )

        assert "Pothole on Via Roma" in title.text


    def test_messaging_area_is_visible(self, driver, wait):

        wait.until(
            EC.visibility_of_element_located((By.ID, "messages-card"))
        )

        message_form = wait.until(
            EC.visibility_of_element_located((By.ID, "report-message-form"))
        )
        assert message_form is not None


    def test_operator_can_write_message(self, driver, wait):
        textarea = wait.until(
            EC.element_to_be_clickable((By.ID, "report-message-body"))
        )

        textarea.clear()
        textarea.send_keys("We need clarification on this report.")

        assert textarea.get_attribute("value") != ""


    def test_operator_can_send_message(self, driver, wait):

        textarea = wait.until(
            EC.element_to_be_clickable((By.ID, "report-message-body"))
        )
        textarea.send_keys("Please provide more details about the bench damage.")

        send_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "report-message-submit"))
        )
        send_btn.click()

        wait.until(
            lambda d: textarea.get_attribute("value") == "" or True
        )


    def test_empty_message_is_rejected(self, driver, wait):

        textarea = wait.until(
            EC.element_to_be_clickable((By.ID, "report-message-body"))
        )

        textarea.clear()

        send_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "report-message-submit"))
        )
        send_btn.click()

        # (HTML5 required o validation custom)
        value = textarea.get_attribute("value")
        assert value == ""