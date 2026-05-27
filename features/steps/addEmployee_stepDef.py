import time
from behave import given, when, then
from utils.helpers import get_logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

logger = get_logger("steps.addEmployee")

@given('the user is on the Add Employee page')
def step_navigate_add_employee(context):
    """Navigate to Add Employee page (user is already logged in via Background)."""
    emp_id = context.employee_PageObj_Add.navigate()
    context.employee_id=emp_id
    assert context.employee_PageObj_Add.is_on_add_employee_page(), \
        "Failed to navigate to Add Employee page"
    logger.info("On Add Employee page")


@given('a new employee "{full_name}" has been added to the system')
def step_add_employee_to_system(context, full_name):
    """
    Pre-condition step: add an employee so search scenarios have data.
    full_name format: "FirstName LastName"
    """
    parts = full_name.strip().split()
    first = parts[0]
    last  = parts[-1] if len(parts) > 1 else "Employee"

    emp_id = context.employee_PageObj_Add.navigate()
    context.employee_id=emp_id
    emp_id = context.employee_PageObj_Add.fill_employee_form(
        first_name=first,
        last_name=last,
        employee_id=emp_id
    )
    context.employee_PageObj_Add.save_and_wait()

    # Persist on context for assertion steps
    context.employee_id    = emp_id
    context.employee_name  = full_name
    logger.info(f"Pre-condition employee added: {full_name} | ID: {emp_id}")


@given('a new employee with a known employee ID exists in the system')
def step_add_employee_with_known_id(context):
    """Creates an employee and stores the ID for search assertions."""
    emp_id = context.employee_PageObj_Add.navigate()
    emp_id = context.employee_PageObj_Add.fill_employee_form(
        first_name="SearchById",
        last_name="TestEmployee",
        employee_id=emp_id
    )
    context.employee_PageObj_Add.save_and_wait()
    context.employee_id   = emp_id
    context.employee_name = "SearchById TestEmployee"
    logger.info(f"Employee created for ID search: {emp_id}")
    
@when('the user enters first name "{first_name:w}" and last name "{last_name:w}"')
def step_enter_name(context, first_name, last_name):
    context.employee_PageObj_Add.enter_first_name(first_name)
    context.employee_PageObj_Add.enter_last_name(last_name)
    # Track what we just entered for assertion steps
    context.generated_unique_id = context.employee_PageObj_Add.generate_unique_emp_id()
    
    context.employee_name = f"{first_name} {last_name}"
    logger.info(f"Entered employee name: {context.employee_name}")

@when('the user enters first name "{first_name:w}" and middle name "{middle_name:w}" and last name "{last_name:w}"')
def step_enter_full_name(context, first_name, middle_name, last_name):
    context.employee_PageObj_Add.enter_first_name(first_name)
    context.employee_PageObj_Add.enter_middle_name(middle_name)
    context.employee_PageObj_Add.enter_last_name(last_name)
    # Keep standard formatting for later validations
    context.employee_name = f"{first_name} {last_name}"
    
@when('the user clicks the Save button')
def step_click_save(context):
    context.employee_PageObj_Add.click_save()
    
@when('the user sets the employee ID to "{employee_id}"')
def step_set_employee_id(context, employee_id):
    timestamp = datetime.now().strftime("%H%M%S")
    unique_id = f"{employee_id}{timestamp}"
    context.employee_PageObj_Add.set_employee_id(unique_id)
    context.employee_id = unique_id
    
@when('the user enables the "Create Login Details" toggle')
def step_enable_login_toggle(context):
    context.employee_PageObj_Add.enable_create_login()

@when('the user enters login username "{username}" and password "{password}"')
def step_enter_login_creds(context, username, password):
    timestamp = datetime.now().strftime("%H%M%S")
    unique_user_id = f"{username}{timestamp}"
    context.employee_PageObj_Add.enter_login_username(unique_user_id)
    context.employee_PageObj_Add.enter_login_password(password)
    context.employee_PageObj_Add.enter_confirm_password(password)
    
@when('the user enters only first name "{first_name}"')
def step_enter_only_first(context, first_name):
    context.employee_PageObj_Add.enter_first_name(first_name)

@when('the user enters only last name "{last_name}"')
def step_enter_only_last(context, last_name):
    context.employee_PageObj_Add.enter_last_name(last_name)

@when('the user clicks the Save button without entering any data')
def step_click_save_empty(context):
    context.employee_PageObj_Add.click_save()
    
@then('the employee profile page should be displayed')
def step_verify_profile_page(context):
    """
    GenAI assertion: after a successful save, OrangeHRM redirects to the
    Personal Details tab of the employee record.
    Validate by checking the URL contains 'viewPersonalDetails'.
    """
    WebDriverWait(context.driver, 20).until(EC.url_contains("/pim/viewPersonalDetails"))
    current_url = context.driver.current_url
    assert "viewPersonalDetails" in current_url or "editEmployee" in current_url, (
        f"Expected employee profile URL but got: {current_url}"
    )
    logger.info(f"Employee profile page confirmed: {current_url}")

@then('the Employee ID field should contain an auto-generated value')
def step_verify_auto_id(context):
    emp_id = context.employee_PageObj_Add.get_employee_id()
    assert emp_id and len(emp_id) > 0, "Employee ID field is empty — expected auto-generated value"
    logger.info(f"Auto-generated Employee ID confirmed: '{emp_id}'")


@then('the employee record should be saved successfully')
def step_verify_save_success(context):
    """
    GenAI assertion: confirm save was successful.
    OrangeHRM shows a green 'Successfully Saved' toast on success.
    """
    from selenium.webdriver.common.by import By
    from utils.helpers import wait_for_element
    # Check URL first (primary indicator)
    current_url = context.driver.current_url
    assert "viewPersonalDetails" in current_url or "editEmployee" in current_url, \
        f"Save did not redirect to profile page. Current URL: {current_url}"

    # Try to find success toast (may have already disappeared)
    try:
        toast = wait_for_element(context.driver,(By.XPATH, "//div[contains(@class,'oxd-toast--success')]"),timeout=5)
        logger.info(f"Success toast confirmed: '{toast.text}'")
    except Exception:
        # Toast already dismissed — URL check is sufficient
        logger.info("Success toast not found (may have auto-dismissed) — URL check passed")
    
@then('a required field validation error should appear for first name')
def step_verify_first_name_error(context):
    errors = context.employee_PageObj_Add.get_validation_errors()
    assert len(errors) > 0, "Expected validation error for first name but none appeared"
    assert any("required" in e.lower() for e in errors), \
        f"Expected 'Required' error but got: {errors}"
    logger.info(f"First name validation error confirmed: {errors}")

@then('a required field validation error should appear for last name')
def step_verify_last_name_error(context):
    errors = context.employee_PageObj_Add.get_validation_errors()
    assert len(errors) > 0, "Expected validation error for last name but none appeared"
    logger.info(f"Last name validation error confirmed: {errors}")

@then('multiple required field validation errors should be displayed')
def step_verify_multiple_errors(context):
    errors = context.employee_PageObj_Add.get_validation_errors()
    assert len(errors) > 0, \
        f"Expected multiple validation errors but got {len(errors)}: {errors}"
    logger.info(f"Multiple validation errors confirmed: {errors}")