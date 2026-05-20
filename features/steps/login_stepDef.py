import os
from behave import given, when, then
from utils.helpers import get_logger
from config.settings import settings
from selenium.webdriver.common.by import By
from utils.helpers import wait_for_element

logger = get_logger("steps.login")

@given('the user is logged into the OrangeHRM application')

def step_user_logged_in(context):
    """
    Background step: logs in as User before every scenario that needs it.
    This is the shared precondition for most scenarios in this feature.
    """
    context.login_PageObj.login_and_wait_for_dashboard()
    logger.info("Background: User logged in successfully")


# @given('the user navigates to the OrangeHRM login page')
# def step_navigate_to_login(context):
#     context.login_PageObj.navigate()
#     context.login_PageObj.login_and_wait_for_dashboard()
#     logger.info("Background: Admin logged in successfully")

@given('the user navigates to the OrangeHRM login page')
def step_navigate_to_login(context):
    context.login_PageObj.navigate()


# ─────────────────────────────────────────────────────────────────────────────
# WHEN steps
# ─────────────────────────────────────────────────────────────────────────────

@when('the user enters correct credentials')
def step_enter_credentials(context):
    use_env = os.getenv("USE_ENV_CREDENTIALS", "1").lower() in ("1", "true", "yes")
    if use_env:
        username = settings.USERNAME
        password = settings.PASSWORD
    else:
        username = getattr(context, "feature_username", None)
        password = getattr(context, "feature_password", None)
        # fallback to settings if feature did not provide values
        username = username or settings.USERNAME
        password = password or settings.PASSWORD

    login_PageObj = getattr(context, "login_PageObj", None)
    if not login_PageObj:
        raise RuntimeError("context.login_PageObj not found. Ensure features/environment.py sets context.login_PageObj")

    # Debug-safe log (masked)
    masked = username if not username or len(username) <= 4 else username[0] + "***" + username[-1]
    logger.info("Using username (masked): %s", masked)

    login_PageObj.enter_username(username)
    login_PageObj.enter_password(password)

@when('the user enters incorrect credentials')
def step_enter_incorrect_credentials(context):
    context.login_PageObj.enter_username("invalid_user")
    context.login_PageObj.enter_password("invalid_pass")

@when('the user clicks the Login button')
def step_click_login(context):
    context.login_PageObj.click_login()
    
@when('the user submits the login form with empty credentials')
def step_submit_empty_login(context):
    """Click login without entering any username or password."""
    context.login_PageObj.navigate()
    context.login_PageObj.click_login()

@then('the user should be redirected to the Dashboard page')
def step_check_dashboard_redirect(context):
    assert "dashboard" in context.driver.current_url.lower(), (f"Expected 'dashboard' in URL but got: {context.driver.current_url}")

@then('the Dashboard header should be visible')
def step_check_dashboard_header(context):
    """
    GenAI assertion: validate that the Dashboard header / page title is visible
    after a successful login, confirming the user is authenticated.
    """
    # OrangeHRM shows "Dashboard" text in the top breadcrumb after login
    header = context.home_PageObj.get_dashboard_header(timeout=5)
    assert header is not None, "Dashboard header not found after login"
    logger.info(f"Dashboard header confirmed: '{header.text}'")

@then('an error message "{expected_text}" should be displayed')
def step_check_error_message(context, expected_text):
    login_PageObj = getattr(context, "login_PageObj", None)
    if not login_PageObj:
        raise RuntimeError("context.login_PageObj not found. Ensure features/environment.py sets context.login_PageObj")
    assert login_PageObj.is_error_displayed(), f"Expected error message visible: {expected_text}"
    assert expected_text in login_PageObj.get_error_message()
    
@then('the user should remain on the login page')
def step_check_still_on_login(context):
    assert context.login_PageObj.is_on_login_PageObj(), (
        f"Expected login page URL but got: {context.driver.current_url}"
    )

@then('required field validation errors should be displayed')
def step_check_required_field_errors(context):
    """
    GenAI assertion: OrangeHRM marks empty required inputs with
    'Required' span messages. Assert at least one is visible.
    """
    assert context.login_PageObj.is_required_field_error_displayed(), \
        "Expected 'Required' field validation error but none appeared"
    logger.info("Required field validation error confirmed")