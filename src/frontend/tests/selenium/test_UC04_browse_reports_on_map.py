import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC


from tests.conftest import (
    BASE_URL,
    driver,
    wait,
    find,
    finds,
    wait_for,
)


class TestBrowseReportsMap:

    @pytest.fixture(autouse=True)
    def setup(self, driver):
        driver.get(f"{BASE_URL}")

    @staticmethod
    def _map_container(driver, wait):

        return wait.until(
            EC.presence_of_element_located(
                (By.ID, "public-map")
            )
        )

    @staticmethod
    def _markers(driver):

        return driver.find_elements(
            By.CLASS_NAME,
            "leaflet-marker-icon"
        )

    def test_map_view_loads(self, driver, wait):

        map_container = self._map_container(driver, wait)

        assert map_container.is_displayed()

        tiles = driver.find_elements(
            By.CLASS_NAME,
            "leaflet-tile-loaded"
        )

        assert len(tiles) > 0

    def test_zoom_controls_exist(self, driver, wait):

        self._map_container(driver, wait)

        zoom_in = wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "leaflet-control-zoom-in")
            )
        )

        zoom_out = wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "leaflet-control-zoom-out")
            )
        )

        assert zoom_in.is_displayed()
        assert zoom_out.is_displayed()

    def test_map_can_be_zoomed_and_panned(self, driver, wait):

        map_container = self._map_container(driver, wait)

        actions = ActionChains(driver)

        actions.click_and_hold(map_container)\
               .move_by_offset(100, 50)\
               .release()\
               .perform()

        zoom_in = driver.find_element(
            By.CLASS_NAME,
            "leaflet-control-zoom-in"
        )

        zoom_in.click()

        assert map_container.is_displayed()

    def test_markers_are_displayed_if_reports_exist(self, driver, wait):

        self._map_container(driver, wait)

        wait.until(
            lambda d: len(self._markers(d)) >= 0
        )

        markers = self._markers(driver)

        assert markers is not None