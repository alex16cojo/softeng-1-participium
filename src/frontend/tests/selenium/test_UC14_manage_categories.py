import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from tests.conftest import (
    BASE_URL,
    ADMIN_USER,
    ADMIN_PASSWORD,
    driver,
    wait,
    wait_for,
    finds,
    ensure_logged_out,
    login
)


class TestManageCategories:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        driver.get(f"{BASE_URL}")
        ensure_logged_out(driver, wait)

        login(driver, wait, ADMIN_USER, ADMIN_PASSWORD)

        wait_for(wait, "admin-categories-section")

    def test_admin_can_create_new_configuration(self, driver, wait):
        unique_suffix = int(time.time())
        new_category_name = f"QA Category {unique_suffix}"
        new_username = f"qa_user_{unique_suffix}"
        new_email = f"qa_{unique_suffix}@example.com"

        # creo una nuova categoria
        category_input = wait_for(wait, "admin-new-category-name")
        category_input.send_keys(new_category_name)

        wait_for(wait, "admin-new-category-submit").click()

        time.sleep(2)

        category_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[id^="admin-category-name-"]')
        category_names = [inp.get_attribute("value") for inp in category_inputs]
        assert new_category_name in category_names, f"La categoria {new_category_name} non è stata trovata."

        # creo un nuovo utente
        wait_for(wait, "admin-new-user-username").send_keys(new_username)
        wait_for(wait, "admin-new-user-first-name").send_keys("Mario")
        wait_for(wait, "admin-new-user-last-name").send_keys("Rossi")
        wait_for(wait, "admin-new-user-email").send_keys(new_email)
        wait_for(wait, "admin-new-user-password").send_keys("Password123!")

        role_dropdown = Select(wait_for(wait, "admin-new-user-role"))
        role_dropdown.select_by_value("citizen")


        wait_for(wait, "admin-new-user-submit").click()

        time.sleep(2)

        email_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="email"][id^="admin-user-email-"]')
        user_emails = [inp.get_attribute("value") for inp in email_inputs]
        assert new_email in user_emails

    def test_create_already_existing_category(self, driver, wait):
        duplicate_name = "Other"

        category_input = wait_for(wait, "admin-new-category-name")
        category_input.send_keys(duplicate_name)

        wait_for(wait, "admin-new-category-submit").click()

        error_message = wait_for(wait, "admin-error")

        assert error_message.is_displayed()
        assert len(error_message.text) > 0

    @pytest.mark.implementation_bug(
        reason="BUG-UC14: The system allows the deactivation of a category with associated reports, displaying a success message."
    )
    def test_deactivate_category_with_associated_reports(self, driver, wait):
        category_id = "7"

        active_checkbox = wait_for(wait, f"admin-category-active-{category_id}")

        if active_checkbox.is_selected():
            active_checkbox.click()

        wait_for(wait, f"admin-category-save-{category_id}").click()

        time.sleep(1)

        error_elements = finds(driver, "admin-error")
        assert len(error_elements) > 0