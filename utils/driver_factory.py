import logging
import os
import sys
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service  import Service as ChromeService
from selenium.webdriver.chrome.options  import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService 
from selenium.webdriver.edge.service import Service as EdgeService 
from selenium.webdriver.firefox.options import Options as FirefoxOptions 
from selenium.webdriver.edge.options import Options as EdgeOptions 
from config.settings import settings 
from utils.helpers import get_logger 

logger = get_logger(__name__) 

class DriverFactory: 
    """ Factory class that creates a configured WebDriver instance. """ 

    @staticmethod
    def get_driver() -> webdriver.Remote:
        browser = settings.BROWSER.lower() 
        logger.info(f"Launching browser: {browser} | Headless: {settings.HEADLESS}") 

        if browser == "chrome":
            driver = DriverFactory._get_chrome_driver()
        elif browser == "firefox":
            driver = DriverFactory._get_firefox_driver()
        elif browser == "edge":
            driver = DriverFactory._get_edge_driver()
        else:
            raise ValueError(f"Unsupported browser: '{browser}'. Use chrome, firefox, or edge") 

        driver.implicitly_wait(settings.IMPLICIT_WAIT) 
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT) 
        
        if not settings.HEADLESS:
            try:
                driver.set_window_size(settings.BROWSER_WIDTH, settings.BROWSER_HEIGHT)
            except Exception:
                logger.debug("Could not set window size layout")

        logger.info(f"Browser started successfully for: {browser}")
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
        if os.getenv("GITHUB_ACTIONS") == "true":
            actions_driver_dir = os.getenv("CHROMEWEBDRIVER")
            driver_path = os.path.join(actions_driver_dir, "chromedriver") if actions_driver_dir else "/usr/local/bin/chromedriver"
            logger.info(f"CI environment detected. Using driver path: {driver_path}")
            return webdriver.Chrome(service=ChromeService(executable_path=driver_path), options=options)

        # Scenario 2: Explicit Local Settings Configuration
        configured = getattr(settings, "CHROMEDRIVER_PATH", None)
        if configured:
            logger.info("Using configured CHROMEDRIVER_PATH: %s", configured)
            if os.path.isfile(configured):
                return DriverFactory._start_chrome_with_path(configured, options)
            logger.warning("Configured CHROMEDRIVER_PATH does not exist: %s", configured)

        # Scenario 3: Selenium 4 Built-in Selenium Manager
        try:
            logger.info("Launching browser via native Selenium Manager.") 
            driver = webdriver.Chrome(options=options) 
            if not settings.HEADLESS:
                driver.maximize_window() 
            return driver
        except Exception:
            logger.error("All Chrome launch strategies failed:\n%s", traceback.format_exc()) 
            raise

    @staticmethod
    def _start_chrome_with_path(driver_path: str, options: ChromeOptions) -> webdriver.Chrome:
        """Helper to validate path and start Chrome service cleanly."""
        if os.name == "nt" and not driver_path.lower().endswith(".exe"):
            msg = (
                f"Chromedriver at '{driver_path}' is not a Windows executable (.exe).\n" 
                "This will cause WinError 193 when starting the service.\n" 
            )
            logger.error(msg)
            raise OSError(msg)

        try:
            service = ChromeService(driver_path)
            driver = webdriver.Chrome(service=service, options=options) 
            if not settings.HEADLESS:
                driver.maximize_window()
            return driver
        except OSError as e:
            # Surface more useful diagnostic info for WinError 193
            logger.error("Failed to start chromedriver process. Path: %s\nException: %s", driver_path, e)
            raise

    @staticmethod 
    def _get_firefox_driver() -> webdriver.Firefox: 
        options = FirefoxOptions() 
        if settings.HEADLESS: 
            options.add_argument("--headless") 
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")

        # Scenario 1: Explicit Local Settings Configuration
        configured = getattr(settings, "GECKODRIVER_PATH", None) 
        if configured: 
            logger.info("Using configured GECKODRIVER_PATH: %s", configured) 
            if os.path.isfile(configured): 
                return webdriver.Firefox(service=FirefoxService(executable_path=configured), options=options)
            logger.warning("Configured GECKODRIVER_PATH does not exist: %s. Falling back.", configured)

        # Scenario 2: Selenium 4 Built-in Selenium Manager
        try: 
            logger.info("Launching Firefox via native Selenium Manager.") 
            driver = webdriver.Firefox(options=options) 
            if not settings.HEADLESS:
                driver.maximize_window() 
            return driver 
        except Exception:
            logger.error("All Firefox launch strategies failed:\n%s", traceback.format_exc())
            raise

    @staticmethod 
    def _get_edge_driver() -> webdriver.Edge: 
        options = EdgeOptions() 
        if settings.HEADLESS: 
            options.add_argument("--headless=new") 
            options.add_argument("--window-size=1920,1080") 
            options.add_argument("--no-sandbox") 
            options.add_argument("--disable-dev-shm-usage") 
            options.add_argument("--disable-gpu")

        # Scenario 1: Explicit Local Settings Configuration
        configured = getattr(settings, "EDGEDRIVER_PATH", None) 
        if configured: 
            logger.info("Using configured EDGEDRIVER_PATH: %s", configured) 
            if os.path.isfile(configured): 
                return webdriver.Edge(service=EdgeService(executable_path=configured), options=options)
            logger.warning("Configured EDGEDRIVER_PATH does not exist: %s. Falling back.", configured)

        # Scenario 2: Selenium 4 Built-in Selenium Manager
        try: 
            logger.info("Launching Edge via native Selenium Manager.") 
            driver = webdriver.Edge(options=options) 
            if not settings.HEADLESS:
                driver.maximize_window() 
            return driver 
        except Exception:
            logger.error("All Edge launch strategies failed:\n%s", traceback.format_exc())
            raise