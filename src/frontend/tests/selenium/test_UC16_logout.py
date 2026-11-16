import pytest
from selenium.webdriver.common.by import By

from tests.conftest import (
    BASE_URL,
    CITIZEN_USER,
    CITIZEN_PASSWORD,
    driver,
    wait,
    wait_for,
    ensure_logged_out,
    login
)


class TestLogout:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        driver.get(f"{BASE_URL}")
        ensure_logged_out(driver, wait)

        login(driver, wait, CITIZEN_USER, CITIZEN_PASSWORD)
        wait_for(wait, "logout-button")

    def test_citizen_can_logout_successfully(self, driver, wait):
        wait_for(wait, "logout-button").click()

        wait_for(wait, "nav-login")

        protected_url = f"{BASE_URL}/dashboard"
        driver.get(protected_url)

        wait_for(wait, "login-page")
        assert "login" in driver.current_url.lower()

    def test_session_already_expired_redirects_to_public_area(self, driver, wait):
        # elimino manualmente i cookie
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")

        protected_url = f"{BASE_URL}/dashboard"
        driver.get(protected_url)

        wait_for(wait, "login-page")
        assert "login" in driver.current_url.lower()