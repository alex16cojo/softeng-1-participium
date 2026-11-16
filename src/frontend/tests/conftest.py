import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import random as rd
from pathlib import Path

BASE_URL = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
IMPLICIT_WAIT = 5
EXPLICIT_WAIT = 10

CITIZEN_USER = "citizen@example.com"
OPERATOR_USER = "operator@example.com"
ADMIN_USER = "admin@example.com"
CITIZEN_PASSWORD = "Citizen123!"
OPERATOR_PASSWORD = "Operator123!"
ADMIN_PASSWORD = "Admin123!"


@pytest.fixture(scope="session")
def driver():

    options = webdriver.ChromeOptions()
    if os.getenv("CI"):
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--guest")

    d = webdriver.Chrome(options=options)
    d.implicitly_wait(IMPLICIT_WAIT)
    yield d
    d.quit()


@pytest.fixture()
def wait(driver):
    return WebDriverWait(driver, EXPLICIT_WAIT)


def by_id(id):
    return By.ID, id


def find(driver, id):
    return driver.find_element(By.ID, id)


def finds(driver, id):
    return driver.find_elements(By.ID, id)


def wait_for(wait, id):
    return wait.until(EC.visibility_of_element_located(by_id(id)))


def wait_clickable(wait, id):
    return wait.until(EC.element_to_be_clickable(by_id(id)))


def login(driver, wait, username, password):
    driver.get(BASE_URL)
    wait_for(wait, "login-link")

    find(driver, "login-link").click()

    wait_for(wait, "login-identifier")
    wait_for(wait, "login-password")

    username_input = find(driver, "login-identifier")
    clear_input(username_input)
    username_input.send_keys(username)

    password_input = find(driver, "login-password")
    clear_input(password_input)
    password_input.send_keys(password)

    find(driver, "login-submit").click()

    wait_for(wait, "logout-button")


def logout(driver, wait):
    wait_for(wait, "logout-button")
    find(driver, "logout-button").click()
    wait_for(wait, "login-submit")


def go_home(driver, wait):
    wait_for(wait, "nav-home")
    find(driver, "nav-home").click()
    wait_for(wait, "home-hero-title")


def ensure_logged_out(driver, wait):
    driver.get(BASE_URL)
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(by_id("nav-login"))
        )
    except Exception:
        logout(driver, wait)


def return_random_value(min: int, max: int):
    return rd.randint(min, max)


# selenium .clear() ha problemi con form controllati di React
def clear_input(input):
    input.click()
    input.send_keys(Keys.CONTROL, "a")
    input.send_keys(Keys.DELETE)


def get_photos_paths():
    photos_directory_path = Path(__file__).parent / "selenium" / "test_photos"

    _image_1 = photos_directory_path / "road.jpg"
    _image_2 = photos_directory_path / "traffic_sign.jpg"
    _image_3 = photos_directory_path / "waste.jpg"
    _image_4 = photos_directory_path / "traffic_light.jpg"

    return [str(_image_1.resolve()), str(_image_2.resolve()), str(_image_3.resolve()), str(_image_4.resolve())]
