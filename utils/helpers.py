import os
import logging
import time
import re
from datetime import datetime
from pathlib import Path

import colorlog
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from config.settings import settings


# ─────────────────────────────────────────────────────────────────────────────
# Logger Setup
# ─────────────────────────────────────────────────────────────────────────────

def get_logger(name: str) -> logging.Logger:
    """
    Returns a coloured console logger.
    Log level is read from settings (INFO by default).
    """
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s[%(levelname)s]%(reset)s %(name)s — %(message)s",
        log_colors={
            "DEBUG":    "cyan",
            "INFO":     "green",
            "WARNING":  "yellow",
            "ERROR":    "red",
            "CRITICAL": "bold_red",
        }
    ))
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Screenshot Helper
# ─────────────────────────────────────────────────────────────────────────────

def take_screenshot(driver: WebDriver, name: str = "screenshot") -> str:
    """
    Captures a PNG screenshot and saves it to screenshots/<timestamp>_<name>.png
    Returns the absolute path to the saved file.
    """
    screenshots_dir = Path(settings.SCREENSHOTS_DIR)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitise name so it is safe as a filename
    safe_name = re.sub(r"[^\w\-]", "_", name)
    filename = screenshots_dir / f"{timestamp}_{safe_name}.png"

    try:
        driver.save_screenshot(str(filename))
        logger.info(f"Screenshot saved -> {filename}")
    except Exception as exc:
        logger.error(f"Could not save screenshot: {exc}")

    return str(filename)


def take_failure_screenshot(driver: WebDriver, scenario_name: str) -> str:
    """Convenience wrapper — prefixes name with 'FAIL_'."""
    return take_screenshot(driver, name=f"FAIL_{scenario_name}")


# ─────────────────────────────────────────────────────────────────────────────
# Wait Helpers
# ─────────────────────────────────────────────────────────────────────────────

def wait_for_element(driver: WebDriver, locator: tuple, timeout: int = None):
    """
    Explicit wait until an element is visible.
    locator: (By.XXX, "value")
    """
    timeout = timeout or settings.EXPLICIT_WAIT
    try:
        element = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
        return element
    except TimeoutException:
        logger.error(f"Element not found after {timeout}s: {locator}")
        raise


def wait_for_clickable(driver: WebDriver, locator: tuple, timeout: int = None):
    """Explicit wait until an element is clickable."""
    timeout = timeout or settings.EXPLICIT_WAIT
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def wait_for_url_contains(driver: WebDriver, partial_url: str, timeout: int = None):
    """Wait until current URL contains a substring."""
    timeout = timeout or settings.EXPLICIT_WAIT
    WebDriverWait(driver, timeout).until(EC.url_contains(partial_url))


def wait_for_text_in_element(driver: WebDriver, locator: tuple, text: str, timeout: int = None):
    """Wait until an element contains the expected text."""
    timeout = timeout or settings.EXPLICIT_WAIT
    return WebDriverWait(driver, timeout).until(EC.text_to_be_present_in_element(locator, text))

def short_sleep(seconds: float = 1.0):
    """Small deliberate sleep — use sparingly, prefer explicit waits."""
    time.sleep(seconds)


# ─────────────────────────────────────────────────────────────────────────────
# Data Helpers
# ─────────────────────────────────────────────────────────────────────────────

def generate_unique_name(prefix: str = "Employee") -> str:
    """Returns a name with a millisecond timestamp suffix to avoid collisions."""
    ts = datetime.now().strftime("%H%M%S%f")[:10]
    return f"{prefix}_{ts}"