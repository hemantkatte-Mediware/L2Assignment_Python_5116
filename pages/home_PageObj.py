from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.settings import settings
from utils.helpers import get_logger, wait_for_url_contains, wait_for_element

logger = get_logger(__name__)

class HomePage(BasePage):
    """
    Encapsulates all interactions with the home page.
    """
    # ── Locators ──────────────────────────────────────────────────────────────
    DASHBOARD_HEADER = (By.XPATH, "//h6[contains(normalize-space(.), 'Dashboard')]")

    def get_dashboard_header(self, timeout: int = 15):
        """
        Return the Dashboard header element after login, or None if not found.
        Encapsulates the locator/timeout logic so steps remain simple.
        """
        return wait_for_element(self.driver, self.DASHBOARD_HEADER, timeout=timeout)
