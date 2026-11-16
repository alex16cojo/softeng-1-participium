import pytest
from tests.conftest import (
    BASE_URL,
    driver,
    wait,
    find,
    finds,
    wait_for,
    login,
    logout,
    ensure_logged_out,
    go_home,
    return_random_value
)


class TestRegister:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        ensure_logged_out(driver, wait)

    def test_register_citizen(self, driver, wait):

        account_unique_id_string = str(return_random_value(1, 1000000))
        account_email = "citizen" + account_unique_id_string + "@example.com"
        account_password = "password123!"

        go_home(driver, wait)
        ensure_logged_out(driver, wait)

        wait_for(wait, "register-link")
        find(driver, "register-link").click()

        wait_for(wait, "register-submit")

        username_input = find(driver, "register-username")
        username_input.clear()
        username_input.send_keys("citizen" + account_unique_id_string + ".username")

        first_name_input = find(driver, "register-first-name")
        first_name_input.clear()
        first_name_input.send_keys("luca")

        last_name_input = find(driver, "register-last-name")
        last_name_input.clear()
        last_name_input.send_keys("verdi")

        email_input = find(driver, "register-email")
        email_input.clear()
        email_input.send_keys(account_email)

        # test campo mancante
        find(driver, "register-submit").click()
        assert driver.current_url.startswith(BASE_URL + "/register")

        password_input = find(driver, "register-password")
        password_input.clear()
        password_input.send_keys(account_password)

        find(driver, "register-submit").click()

        wait_for(wait, "register-success")
        wait_for(wait, "verification-box")
        assert find(driver, "register-success").text == "Account created for " + account_email + ". Verify the email before logging in."

        find(driver, "verification-link").click()  # porta ad una pagina di verifica

        driver.get(BASE_URL)
        wait_for(wait, "login-link")

        ensure_logged_out(driver, wait)
        login(driver, wait, account_email, account_password)

        assert find(driver, "profile-section") is not None
        assert find(driver, "my-reports-card") is not None
        assert find(driver, "notifications-card") is not None
