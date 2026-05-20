from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.settings import settings
from utils.helpers import get_logger, wait_for_url_contains, wait_for_element

logger = get_logger(__name__)

class LoginPage(BasePage):
    """
    Encapsulates all interactions with the login page.
    """

    # ── URL ───────────────────────────────────────────────────────────────────
    LOGIN_URL = f"{settings.BASE_URL}/web/index.php/auth/login"

    # ── Locators ──────────────────────────────────────────────────────────────
    # GenAI-assisted locator generation for OrangeHRM login form:

    USERNAME_INPUT   = (By.NAME,  "username")
    PASSWORD_INPUT   = (By.NAME,  "password")
    LOGIN_BUTTON     = (By.XPATH, "//button[@type='submit']")
    LOGIN_TITLE      = (By.XPATH, "//h5[contains(@class,'oxd-text') and text()='Login']")
    ERROR_MESSAGE    = (By.XPATH, "//p[contains(@class,'oxd-alert-content-text')]")
    FORGOT_PASSWORD  = (By.XPATH, "//p[text()='Forgot your password? ']//following-sibling::a")
    OHR_LOGO         = (By.XPATH, "//img[contains(@src,'orangehrm_logo')]")
    REQUIRED_FIELD   = (By.XPATH, "//span[contains(@class,'oxd-input-field-error-message')]")

    # ── Actions ───────────────────────────────────────────────────────────────

    def navigate(self):
        """Open the login URL directly."""
        self.open(self.LOGIN_URL)
        # wait for the page to be ready
        self.find_element(self.USERNAME_INPUT)
        logger.info("Login page loaded")

    def enter_username(self, username: str):
        self.type_text(self.USERNAME_INPUT, username)

    def enter_password(self, password: str):
        self.type_text(self.PASSWORD_INPUT, password)

    def click_login(self):
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str = None, password: str = None):
        """
        Full login flow.
        Defaults to Admin credentials from settings if not provided.
        """
        username = username or settings.USERNAME
        password = password or settings.PASSWORD

        logger.info(f"Logging in as: {username}")
        self.navigate()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def login_and_wait_for_dashboard(self, username: str = None, password: str = None):
        """Login and explicitly wait for the dashboard URL."""
        self.login(username, password)
        self.wait_for_url_contains("dashboard")
        logger.info("Dashboard loaded — login successful")

    # ── Assertions / State Checks ─────────────────────────────────────────────

    def get_error_message(self) -> str:
        """Returns the error message text (for negative test assertions)."""
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_displayed(self) -> bool:
        return self.is_element_visible(self.ERROR_MESSAGE, timeout=5)

    def is_required_field_error_displayed(self) -> bool:
        return self.is_element_visible(self.REQUIRED_FIELD, timeout=5)

    def is_on_login_PageObj(self) -> bool:
        return "login" in self.get_current_url().lower()

    def is_logged_in(self) -> bool:
        return "dashboard" in self.get_current_url().lower()