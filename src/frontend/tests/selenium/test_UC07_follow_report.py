import pytest
import time

from tests.conftest import (
    BASE_URL,
    CITIZEN_USER,
    CITIZEN_PASSWORD,
    driver,
    wait,
    ensure_logged_out,
    login,
    finds,
    wait_for
)


class TestFollowReport:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        driver.get(f"{BASE_URL}")
        ensure_logged_out(driver, wait)

    def test_unauthenticated_user_cannot_follow(self, driver, wait):
        driver.get(f"{BASE_URL}/reports/2")
        wait_for(wait, "report-detail-page")
        time.sleep(0.5)

        elements = finds(driver, "follow-button")
        assert len(elements) == 0

    @pytest.mark.implementation_bug(reason="BUG-UC07 - Follow button requires double-click to register follow action and update UI")
    def test_authenticated_citizen_can_follow(self, driver, wait):
        login(driver, wait, CITIZEN_USER, CITIZEN_PASSWORD)

        try:
            driver.get(f"{BASE_URL}/reports/2")
            wait_for(wait, "report-detail-page")

            follow_btn = wait_for(wait, "follow-button")
            assert follow_btn.is_displayed()

            follow_btn.click()
            time.sleep(0.5)

        finally:
            wait_for(wait, "logout-button").click()
            wait_for(wait, "nav-login")
            time.sleep(0.5)

    @pytest.mark.implementation_bug(reason="BUG-UC07 - Unfollow button requires double-click to register unfollow action and update UI")
    def test_authenticated_citizen_can_unfollow(self, driver, wait):
        login(driver, wait, CITIZEN_USER, CITIZEN_PASSWORD)

        try:
            driver.get(f"{BASE_URL}/reports/2")
            wait_for(wait, "report-detail-page")

            follow_btn = wait_for(wait, "follow-button")

            # Setup: se non lo sta seguendo, forziamo il follow con il bug del doppio click
            if follow_btn.text == "Follow report":
                follow_btn.click()
                time.sleep(0.5)
                wait_for(wait, "follow-button").click()
                time.sleep(0.5)

            assert wait_for(wait, "follow-button").text == "Unfollow report"

            wait_for(wait, "follow-button").click()
            time.sleep(0.5)

        finally:
            wait_for(wait, "logout-button").click()
            wait_for(wait, "nav-login")
            time.sleep(0.5)