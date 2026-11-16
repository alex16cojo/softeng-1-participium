import pytest
from tests.conftest import (
    BASE_URL,
    CITIZEN_USER,
    CITIZEN_PASSWORD,
    driver,
    wait,
    find,
    finds,
    wait_for,
    login,
    logout,
    ensure_logged_out,
    go_home,
    return_random_value,
    get_photos_paths
)


class TestProfile:
    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        ensure_logged_out(driver, wait)

    def test_update_profile(self, driver, wait):

        login(driver, wait, CITIZEN_USER, CITIZEN_PASSWORD)

        find(driver, "nav-dashboard").click()

        wait_for(wait, "profile-section")

        email_element = find(driver, "profile-email")
        assert email_element.get_attribute("value") == CITIZEN_USER

        # email non modificabile
        email_element.send_keys(".com")
        assert email_element.get_attribute("value") == CITIZEN_USER

        find(driver, "profile-email-notifications").click()
        find(driver, "profile-picture").send_keys(get_photos_paths()[0])

        find(driver, "profile-save").click()

        assert find(driver, "profile-success").text == "Profile updated."
