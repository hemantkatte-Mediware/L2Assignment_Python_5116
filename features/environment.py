"""
features/environment.py
-----------------------
Behave hooks — setup and teardown for the test suite.

Hooks executed:
  before_all   → global setup (create output directories, configure logging)
  before_scenario → launch browser, instantiate page objects
  after_scenario  → screenshot on failure, quit browser
  after_all       → summary report
"""

import os
import logging
import pdb
import sys
from pathlib import Path
from datetime import datetime

from utils.driver_factory import DriverFactory
from utils.helpers import get_logger, take_failure_screenshot
from pages.login_PageObj import LoginPage
from pages.home_PageObj import HomePage
from pages.pim_PageObj import PIMPage, AddEmployeePage
from config.settings  import settings

logger = get_logger("behave.env")


# ─────────────────────────────────────────────────────────────────────────────
# before_all
# ─────────────────────────────────────────────────────────────────────────────

def before_all(context):
    """
    Runs once before the entire test suite.
    Creates output directories and stores global config on the context.
    """
    
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        # Python <3.7 or other env where reconfigure not available: set env fallback
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        os.environ.setdefault("PYTHONUTF8", "1")
        
    # Create output directories
    for directory in [settings.SCREENSHOTS_DIR, settings.REPORTS_DIR, "allure-results"]:
        Path(directory).mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info(f"  OrangeHRM Automation Suite")
    logger.info(f"  Environment : {settings.ENVIRONMENT}")
    logger.info(f"  Base URL    : {settings.BASE_URL}")
    logger.info(f"  Browser     : {settings.BROWSER}")
    logger.info(f"  Headless    : {settings.HEADLESS}")
    logger.info(f"  Started at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Attach config to context so steps can access it
    context.config_settings = settings


# ─────────────────────────────────────────────────────────────────────────────
# before_scenario
# ─────────────────────────────────────────────────────────────────────────────

def before_scenario(context, scenario):
    """
    Runs before each scenario.
    Launches a fresh browser and instantiates all page objects.
    """
    logger.info(f"\n{'─'*50}")
    logger.info(f"  SCENARIO: {scenario.name}")
    logger.info(f"  Tags    : {', '.join(scenario.tags)}")
    logger.info(f"{'─'*50}")

    # Launch browser
    context.driver = DriverFactory.get_driver()

    # Attach page objects to the context so all steps can use them
    context.login_PageObj           = LoginPage(context.driver)
    context.home_PageObj            = HomePage(context.driver)
    context.pim_PageObj             = PIMPage(context.driver)
    context.employee_PageObj_Search = PIMPage(context.driver)     
    context.employee_PageObj_Add    = AddEmployeePage(context.driver)

    # Storage for data shared between steps within a scenario
    context.employee_id   = None
    context.employee_name = None


# ─────────────────────────────────────────────────────────────────────────────
# after_step  (screenshot on any step failure)
# ─────────────────────────────────────────────────────────────────────────────

def after_step(context, step):
    """
    Captures a screenshot immediately after any FAILED step.
    This gives us the exact screen state at the point of failure.
    """
    if step.status == "failed":
        safe_scenario = context.scenario.name.replace(" ", "_")[:50]
        safe_step     = step.name.replace(" ", "_")[:30]
        screenshot_name = f"FAIL_{safe_scenario}_{safe_step}"

        path = take_failure_screenshot(context.driver, screenshot_name)
        logger.error(f"Step FAILED: '{step.name}'")
        logger.error(f"Screenshot saved: {path}")

        # Attach to Allure if the allure-behave formatter is active
        try:
            import allure
            with open(path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"Failure Screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
        except (ImportError, Exception):
            pass  # Allure not active — that is fine


# ─────────────────────────────────────────────────────────────────────────────
# after_scenario
# ─────────────────────────────────────────────────────────────────────────────

# def after_scenario(context, scenario):
#     """
#     Runs after each scenario.
#     Always quits the browser — even if the scenario failed.
#     """
#     status = "PASSED" if scenario.status == "passed" else "FAILED"
#     logger.info(f"  Result: {status} — {scenario.name}")

#     if hasattr(context, "driver") and context.driver:
#         context.driver.quit()
#         logger.debug("Browser closed")

def after_scenario(context, scenario):
    # ...existing cleanup / reporting code ...

    # Local debug helper:
    # Set KEEP_BROWSER_ON_FAILURE=1 (or "true") to keep the browser open and drop into pdb
    keep_on_fail = os.getenv("KEEP_BROWSER_ON_FAILURE", "false").lower() in ("1", "true", "yes")
    if scenario.status == "failed" and keep_on_fail:
        logger.warning("Scenario failed and KEEP_BROWSER_ON_FAILURE is set — keeping browser open for debugging.")
        try:
            logger.info("Current URL: %s", context.driver.current_url)
        except Exception:
            logger.debug("Could not read current URL from driver")

        # Save an extra screenshot with a consistent name
        try:
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/{timestamp}_DEBUG_{scenario.name.replace(' ', '_')}.png"
            context.driver.save_screenshot(screenshot_path)
            logger.info("Saved debug screenshot: %s", screenshot_path)
        except Exception:
            logger.debug("Failed to save debug screenshot")

        # Enter interactive debugger in the terminal so you can inspect state.
        # Use 'c' to continue execution (this will let after_scenario finish).
        pdb.set_trace()

        # Return without quitting the browser so it remains open for manual inspection.
        return
    
    # Normal teardown: quit the browser if present
    if getattr(context, "driver", None):
        try:
            context.driver.quit()
        except Exception:
            logger.exception("Error while quitting the browser")

# ─────────────────────────────────────────────────────────────────────────────
# after_all
# ─────────────────────────────────────────────────────────────────────────────

def after_all(context):
    """
    Runs once after the entire test suite.
    Prints a brief execution summary.
    """
    logger.info("=" * 60)
    logger.info(f"  Test suite completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"  Reports   → {settings.REPORTS_DIR}/")
    logger.info(f"  Screenshots → {settings.SCREENSHOTS_DIR}/")
    logger.info("=" * 60)