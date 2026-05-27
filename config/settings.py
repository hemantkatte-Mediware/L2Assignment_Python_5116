import os
import logging
import getpass
from pathlib import Path
from dotenv import load_dotenv

# Ensure dotenv is completely loaded before the class initializes
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)

logger = logging.getLogger(__name__)

class Settings:
    # Environmnet
    ENVIRONMENT: str  = os.getenv("ENVIRONMENT", "demo").lower()
    
    # Application
    BASE_URL = os.getenv(f"{ENVIRONMENT.upper()}_URL") or os.getenv("BASE_URL")
    USERNAME = os.getenv("ADMIN_USERNAME") or os.getenv("APP_USERNAME")
    PASSWORD = os.getenv("ADMIN_PASSWORD") or os.getenv("APP_PASSWORD")

    # Browser
    BROWSER: str         = os.environ.get("BROWSER") or os.getenv("BROWSER", "chrome").lower()
    HEADLESS: bool       = (os.environ.get("HEADLESS") or os.getenv("HEADLESS", "false")).lower() == "true"
    
    # Resolution configurations mapped back to direct environment lookups
    BROWSER_WIDTH: int   = int(os.environ.get("BROWSER_WIDTH") or os.getenv("BROWSER_WIDTH", 1920))
    BROWSER_HEIGHT: int  = int(os.environ.get("BROWSER_HEIGHT") or os.getenv("BROWSER_HEIGHT", 1080))

    # ── Timeouts (seconds) ────────────────────────────────────
    IMPLICIT_WAIT: int      = int(os.getenv("IMPLICIT_WAIT", 10))
    EXPLICIT_WAIT: int      = int(os.getenv("EXPLICIT_WAIT", 30))
    PAGE_LOAD_TIMEOUT: int  = int(os.getenv("PAGE_LOAD_TIMEOUT", 60))

    # ── Output Paths ──────────────────────────────────────────
    REPORTS_DIR: str         = os.getenv("REPORTS_DIR", "reports")
    SCREENSHOTS_DIR: str     = os.getenv("SCREENSHOTS_DIR", "screenshots")
    ALLURE_RESULTS_DIR: str  = os.getenv("ALLURE_RESULTS_DIR", "allure-results")

    # ── Misc ──────────────────────────────────────────────────
    ENVIRONMENT: str  = os.getenv("ENVIRONMENT", "demo").lower()
    LOG_LEVEL: str    = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

# Validation & helpful warnings (local/debug convenience)
_system_user = getpass.getuser()
if not settings.USERNAME:
    logger.warning("No USERNAME/ADMIN_USERNAME found in .env or environment. Set APP_USERNAME in your .env file.")
elif settings.USERNAME == _system_user:
    logger.critical("Namespace collision! App username parameters match machine profile (%r).", _system_user)

if not settings.PASSWORD:
    logger.warning("No PASSWORD/ADMIN_PASSWORD found in .env or environment.")
