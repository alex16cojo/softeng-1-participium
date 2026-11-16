import pytest
from selenium.webdriver.support.ui import Select
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


class TestReport:

    @pytest.fixture(autouse=True)
    def setup(self, driver, wait):
        ensure_logged_out(driver, wait)

    def test_create_new_report(self, driver, wait):

        login(driver, wait, CITIZEN_USER, CITIZEN_PASSWORD)

        find(driver, "nav-new-report").click()

        title_input = find(driver, "report-title")
        description_input = find(driver, "report-description")
        category = find(driver, "report-category")
        anonymous = find(driver, "report-anonymous")
        photo_input = find(driver, "report-photos")
        submit_button = find(driver, "new-report-submit")
        photo_label = find(driver, "new-report-selected-photos")
        map = find(driver, "new-report-map")

        current_title = "title"
        title_input.send_keys(current_title)
        description_input.send_keys("description")

        category = Select(category)
        category.select_by_value(str(return_random_value(1, 9)))

        if return_random_value(0, 1):
            anonymous.click()

        map.click()

        # test campo mancante
        assert photo_label.text == "Selected photos: 0"
        submit_button.click()
        assert driver.current_url.startswith(BASE_URL + "/reports/new")

        photo_input.send_keys(get_photos_paths()[0])
        photo_input.send_keys(get_photos_paths()[1])
        photo_input.send_keys(get_photos_paths()[2])
        photo_input.send_keys(get_photos_paths()[3])

        assert find(driver, "new-report-error").text == "A report can contain at most 3 photos. Only the first 3 have been selected."

        assert photo_label.text == "Selected photos: 3"

        submit_button.click()
        wait_for(wait, "status-history-card")

        assert driver.current_url.startswith(BASE_URL + "/reports/")
        report_id = driver.current_url.split("/reports/")[1]

        find(driver, "nav-dashboard").click()
        wait_for(wait, "my-reports-card")
        assert find(driver, "my-report-row-" + str(report_id) + "-title").text == current_title
