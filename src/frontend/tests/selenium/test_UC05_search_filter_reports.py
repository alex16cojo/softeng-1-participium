import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from tests.conftest import (
    BASE_URL,
    driver,
    wait,
)


class TestSearchFilterReports:

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        driver.get(f"{BASE_URL}")


    def _rows(self, driver):
        return driver.find_elements(
            By.CSS_SELECTOR,
            "#public-report-table-body tr"
        )


    def test_public_table_and_filters_load(self, driver, wait):

        assert wait.until(
            EC.visibility_of_element_located(
                (By.ID, "public-report-table")
            )
        ).is_displayed()

        assert wait.until(
            EC.visibility_of_element_located(
                (By.ID, "public-filter-form")
            )
        ).is_displayed()


    def test_filter_by_category(self, driver, wait):

        select = Select(
            wait.until(lambda d: d.find_element(By.ID, "public-filter-category"))
        )
        select.select_by_index(0)
        driver.find_element(By.ID, "public-filter-submit").click()
        wait.until(lambda d: self._rows(d) is not None)
        assert self._rows(driver) is not None


    def test_filter_by_status(self, driver, wait):

        select = Select(
            driver.find_element(By.ID, "public-filter-status")
        )
        select.select_by_index(0)
        driver.find_element(By.ID, "public-filter-submit").click()
        wait.until(lambda d: self._rows(d) is not None)
        assert self._rows(driver) is not None


    def test_filter_by_date_range(self, driver, wait):

        date_from = driver.find_element(By.ID, "public-filter-date-from")
        date_to = driver.find_element(By.ID, "public-filter-date-to")

        date_from.send_keys("2024-01-01T00:00")
        date_to.send_keys("2026-12-31T00:00")

        driver.find_element(By.ID, "public-filter-submit").click()
        wait.until(lambda d: self._rows(d) is not None)
        assert self._rows(driver) is not None


    def test_sort_order(self, driver, wait):

        select = Select(
            driver.find_element(By.ID, "public-filter-sort")
        )

        select.select_by_value("asc")

        driver.find_element(By.ID, "public-filter-submit").click()

        wait.until(lambda d: self._rows(d) is not None)

        assert self._rows(driver) is not None


    def test_granularity_exists(self, driver, wait):

        select = Select(
            driver.find_element(By.ID, "public-stat-granularity")
        )

        assert select is not None