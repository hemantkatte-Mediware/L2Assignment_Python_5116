"""
pages/base_page.py
------------------
Base Page Object — all page classes inherit from this.

Provides:
  • Wrapped Selenium actions (find, click, type, clear+type, select)
  • Explicit-wait versions of every action
  • Screenshot helper
  • URL navigation
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, ElementClickInterceptedException
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from config.settings import settings
from utils.helpers import get_logger, take_screenshot

logger = get_logger(__name__)


class BasePage:
    """
    Parent class for all Page Objects.
    Encapsulates low-level Selenium interactions so that page classes
    can focus on WHAT to do, not HOW to do it.
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait   = WebDriverWait(driver, settings.EXPLICIT_WAIT)

    # ── Navigation ────────────────────────────────────────────────────────────

    def open(self, url: str):
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    # ── Element Finders ───────────────────────────────────────────────────────

    def find_element(self, locator: tuple):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_elements(self, locator: tuple) -> list:
        self.wait.until(EC.presence_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)

    def is_element_present(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def is_element_visible(self, locator: tuple, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ── Actions ───────────────────────────────────────────────────────────────

    def click(self, locator: tuple):
        """Click with fallback to JS-click if intercepted."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        try:
            element.click()
        except ElementClickInterceptedException:
            logger.warning(f"Normal click intercepted on {locator}, trying JS click")
            self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator: tuple, text: str, clear_first: bool = True):
        """Type text into an input field, optionally clearing it first."""
        element = self.find_element(locator)
        if clear_first:
            element.clear()
            element.send_keys(Keys.CONTROL + "a")   # select all
            element.send_keys(Keys.DELETE)
        element.send_keys(text)
        logger.debug(f"Typed '{text}' into {locator}")

    def get_text(self, locator: tuple) -> str:
        return self.find_element(locator).text.strip()

    def get_attribute(self, locator: tuple, attribute: str) -> str:
        return self.find_element(locator).get_attribute(attribute)

    def select_by_visible_text(self, locator: tuple, text: str):
        element = self.find_element(locator)
        Select(element).select_by_visible_text(text)

    def select_by_value(self, locator: tuple, value: str):
        element = self.find_element(locator)
        Select(element).select_by_value(value)

    def hover(self, locator: tuple):
        element = self.find_element(locator)
        ActionChains(self.driver).move_to_element(element).perform()

    def scroll_into_view(self, locator: tuple):
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    # ── Wait Wrappers ─────────────────────────────────────────────────────────

    def wait_for_url_contains(self, partial_url: str):
        self.wait.until(EC.url_contains(partial_url))

    def wait_for_element_invisible(self, locator: tuple):
        self.wait.until(EC.invisibility_of_element_located(locator))

    def wait_for_text(self, locator: tuple, text: str):
        self.wait.until(EC.text_to_be_present_in_element(locator, text))

    # ── Screenshot ────────────────────────────────────────────────────────────

    def take_screenshot(self, name: str = "page") -> str:
        return take_screenshot(self.driver, name)

    # ── Alerts ────────────────────────────────────────────────────────────────

    def accept_alert(self):
        WebDriverWait(self.driver, 5).until(EC.alert_is_present()).accept()

    def dismiss_alert(self):
        WebDriverWait(self.driver, 5).until(EC.alert_is_present()).dismiss()
