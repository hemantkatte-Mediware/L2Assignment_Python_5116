import logging
import os
import sys
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service  import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service    import Service as EdgeService
from selenium.webdriver.chrome.options  import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options    import Options as EdgeOptions
from webdriver_manager.chrome  import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config.settings import settings
from utils.helpers import get_logger

logger = get_logger(__name__)


class DriverFactory:
    """
    Factory class that creates a configured WebDriver instance.
    """

    @staticmethod
    def get_driver() -> webdriver.Remote:
        browser = settings.BROWSER
        logger.info(f"Launching browser: {browser} | Headless: {settings.HEADLESS}")

        if browser == "chrome":
            driver = DriverFactory._get_chrome_driver()
        else:
            raise ValueError(f"Unsupported browser: '{browser}'. Use chrome")

        driver.implicitly_wait(settings.IMPLICIT_WAIT)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        driver.set_window_size(settings.BROWSER_WIDTH, settings.BROWSER_HEIGHT)

        logger.info(f"Browser started: {driver.capabilities.get('browserName', browser)}")
        return driver

    @staticmethod
    def _get_chrome_driver() -> webdriver.Chrome:
        options = ChromeOptions()
        if settings.HEADLESS:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")

        # If user provided an explicit path in settings, prefer it (validate)
        configured = getattr(settings, "CHROMEDRIVER_PATH", None)
        driver_path = None
        if configured:
            logger.info("Using configured CHROMEDRIVER_PATH: %s", configured)
            if os.path.isfile(configured):
                driver_path = configured
            else:
                logger.warning("Configured CHROMEDRIVER_PATH does not exist: %s", configured)

        # Otherwise use webdriver-manager to download/install
        if not driver_path:
            try:
                driver_path = ChromeDriverManager().install()
                logger.info("webdriver-manager installed chromedriver: %s", driver_path)
            except Exception:
                logger.error("webdriver-manager failed to install chromedriver:\n%s", traceback.format_exc())
                raise

        # Sanity checks for Windows executables
        is_windows = os.name == "nt"
        if not os.path.isfile(driver_path):
            raise OSError(f"Chromedriver path does not point to a file: {driver_path}")

        if is_windows and not driver_path.lower().endswith(".exe"):
            # Common cause of WinError 193: returned file isn't an .exe (corrupted zip, dll, txt, etc.)
            msg = (
                f"Chromedriver at '{driver_path}' is not a Windows executable (.exe).\n"
                "This will cause WinError 193 when starting the service.\n"
                "Actions to resolve:\n"
                "  1) Delete the webdriver-manager cache: %USERPROFILE%\\.wdm (Windows) and re-run.\n"
                "  2) Ensure webdriver-manager and selenium are up-to-date: pip install -U webdriver-manager selenium\n"
                "  3) Optionally set CHROMEDRIVER_PATH in your settings to a valid chromedriver.exe matching your Chrome.\n"
            )
            logger.error(msg)
            raise OSError(msg)

        # Try to start the Chrome service and provide a clearer error if it fails
        try:
            service = ChromeService(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            try:
                driver.maximize_window()
            except Exception:
                logger.debug("Could not maximize window (headless or platform restriction)")
            return driver
        except OSError as e:
            # Surface more useful diagnostic info for WinError 193
            logger.error("Failed to start chromedriver process. Path: %s\nException: %s", driver_path, e)
            raise