import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.conftest import (
    wait,
    driver,
    login,
    logout,
    CITIZEN_USER,
    CITIZEN_PASSWORD,
)


class TestReplyToMunicipalOperatorMessage:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):

        login(driver, wait, CITIZEN_USER, CITIZEN_PASSWORD)

        driver.find_element(
            By.ID,
            "my-report-row-1-open-link"
        ).click()

        wait.until(
            EC.presence_of_element_located((By.ID, "report-detail-page"))
        )

        yield

        try:
            driver.find_element(By.ID, "nav-dashboard").click()
        except Exception:
            pass

        logout(driver, wait)

    def test_report_detail_page_opens(self, driver):

        page = driver.find_element(By.ID, "report-detail-page")
        assert page.is_displayed()

    def test_message_thread_is_visible(self, driver):

        messages_card = driver.find_element(By.ID, "messages-card")
        messages_list = driver.find_element(By.ID, "messages-list")

        assert messages_card.is_displayed()
        assert messages_list is not None

    def test_citizen_can_write_reply(self, driver):

        textarea = driver.find_element(By.ID, "report-message-body")

        text = "Additional information about the issue."

        textarea.clear()
        textarea.send_keys(text)

        assert textarea.get_attribute("value") == text

    def test_citizen_can_send_reply(self, driver, wait):

        textarea = driver.find_element(By.ID, "report-message-body")
        send_button = driver.find_element(By.ID, "report-message-submit")

        message = "The problem is still present."

        textarea.clear()
        textarea.send_keys(message)
        send_button.click()

        wait.until(
            EC.presence_of_element_located((By.ID, "messages-list"))
        )

        wait.until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "[id^='message-item-']")) > 0
        )

        messages = driver.find_elements(By.CSS_SELECTOR, "[id^='message-item-']")
        assert any(message in m.text for m in messages)

    def test_empty_reply_is_rejected(self, driver):

        textarea = driver.find_element(By.ID, "report-message-body")
        send_button = driver.find_element(By.ID, "report-message-submit")

        textarea.clear()
        send_button.click()

        assert driver.execute_script(
            "return arguments[0].checkValidity();",
            textarea
        ) is False