import pytest
from selenium.webdriver.common.by import By
from tests.conftest import (
    BASE_URL,
    CITIZEN_USER,
    OPERATOR_USER,
    ADMIN_USER,
    CITIZEN_PASSWORD,
    OPERATOR_PASSWORD,
    ADMIN_PASSWORD,
    driver,
    wait,
    find,
    finds,
    wait_for,
    login,
    logout,
    ensure_logged_out,
)


class TestLogin:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        ensure_logged_out(driver, wait)

    @staticmethod
    def _visible_nav_ids(driver):
        elements = finds(driver, "main-navigation")
        # get the buttons inside it
        elems = driver.find_elements(By.CSS_SELECTOR, "[id='main-navigation'] [id]")
        return {el.get_attribute("id") for el in elems}

    def test_login_citizen(self, driver, wait):

        login(driver, wait, CITIZEN_USER, CITIZEN_PASSWORD)

        assert find(driver, "profile-section") is not None
        assert find(driver, "my-reports-card") is not None
        assert find(driver, "notifications-card") is not None

        assert "User dashboard" in find(driver, "dashboard-title").text

        nav = self._visible_nav_ids(driver)

        assert "nav-home" in nav
        assert "nav-new-report" in nav
        assert "nav-dashboard" in nav
        assert "logout-button" in nav

        logout(driver, wait)

    def test_login_operator(self, driver, wait):

        login(driver, wait, OPERATOR_USER, OPERATOR_PASSWORD)

        assert find(driver, "operator-summary-section") is not None
        assert find(driver, "pending-reports-section") is not None
        assert find(driver, "assigned-reports-section") is not None

        nav = self._visible_nav_ids(driver)

        assert "nav-home" in nav
        assert "nav-dashboard" in nav
        assert "nav-operator" in nav
        assert "logout-button" in nav

        logout(driver, wait)

    def test_login_admin(self, driver, wait):

        login(driver, wait, ADMIN_USER, ADMIN_PASSWORD)

        assert find(driver, "admin-summary-section") is not None
        assert find(driver, "admin-create-user-card") is not None
        assert find(driver, "admin-create-category-card") is not None
        assert find(driver, "admin-users-section") is not None
        assert find(driver, "admin-categories-section") is not None

        assert find(driver, "admin-new-user-submit") is not None
        assert find(driver, "admin-new-category-submit") is not None

        nav = self._visible_nav_ids(driver)

        assert "nav-home" in nav
        assert "nav-dashboard" in nav
        assert "nav-operator" in nav
        assert "nav-admin" in nav
        assert "logout-button" in nav

        logout(driver, wait)
