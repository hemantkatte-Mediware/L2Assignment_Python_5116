import os
import logging
import getpass
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class Settings:
    # Application
    BASE_URL = os.getenv("BASE_URL")
    USERNAME = os.getenv("USERNAME") or os.getenv("ADMIN_USERNAME")
    PASSWORD = os.getenv("PASSWORD") or os.getenv("ADMIN_PASSWORD")

    BROWSER: str         = os.getenv("BROWSER", "chrome").lower()
    HEADLESS: bool       = os.getenv("HEADLESS", "false").lower() == "true"
    BROWSER_WIDTH: int   = int(os.getenv("BROWSER_WIDTH", 1920))
    BROWSER_HEIGHT: int  = int(os.getenv("BROWSER_HEIGHT", 1080))

    # ── Timeouts (seconds) ────────────────────────────────────
    IMPLICIT_WAIT: int      = int(os.getenv("IMPLICIT_WAIT", 10))
    EXPLICIT_WAIT: int      = int(os.getenv("EXPLICIT_WAIT", 30))
    PAGE_LOAD_TIMEOUT: int  = int(os.getenv("PAGE_LOAD_TIMEOUT", 60))

    # ── Output Paths ──────────────────────────────────────────
    REPORTS_DIR: str         = os.getenv("REPORTS_DIR", "reports")
    SCREENSHOTS_DIR: str     = os.getenv("SCREENSHOTS_DIR", "screenshots")
    ALLURE_RESULTS_DIR: str  = os.getenv("ALLURE_RESULTS_DIR", "allure-results")

    # ── Misc ──────────────────────────────────────────────────
    ENVIRONMENT: str  = os.getenv("ENVIRONMENT", "demo")
    LOG_LEVEL: str    = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

# Validation & helpful warnings (local/debug convenience)
_system_user = getpass.getuser()
if not settings.USERNAME:
    logger.warning("No USERNAME/ADMIN_USERNAME found in .env or environment. Set USERNAME in .env to your test account (e.g. Admin).")
elif settings.USERNAME == _system_user:
    logger.warning("USERNAME=%r looks like the OS account (%r). If tests should use the application account (e.g. Admin), set USERNAME in .env explicitly.", settings.USERNAME, _system_user)

if not settings.PASSWORD:
    logger.warning("No PASSWORD/ADMIN_PASSWORD found in .env or environment. Set PASSWORD in .env (local runs only).")