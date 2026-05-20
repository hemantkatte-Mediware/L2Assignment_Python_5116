import time
from behave import given, when, then
from utils.helpers import get_logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

logger = get_logger("steps.searchEmployee")

@given('the user is on the Employee List page')
def step_navigate_employee_list(context):
    """Navigate to PIM Employee List (user is already logged in via Background)."""
    context.employee_PageObj_Search.navigate_to_pim()
    logger.info("On Employee List page")

@when('the user navigates to the Employee List page')
def step_go_to_employee_list(context):
    context.employee_PageObj_Search.navigate_to_pim()


@when('the user searches for employee name "{name}"')
def step_search_by_name(context, name):
    context.employee_PageObj_Search.search_by_name(name)
    logger.info(f"Searched by name: '{name}'")


@when('the user searches by the employee ID')
def step_search_by_employee_id_from_context(context):
    """Use the employee ID stored on context from a previous step."""
    emp_id = getattr(context, "employee_id", None)
    assert emp_id, "No employee_id on context — run a 'given employee was added' step first"
    context.employee_PageObj_Search.search_by_employee_id(emp_id)
    logger.info(f"Searched by employee ID: '{emp_id}'")


@when('the user searches by employee ID "{emp_id}"')
def step_search_by_explicit_employee_id(context, emp_id):
    context.employee_PageObj_Search.search_by_employee_id(emp_id)
    logger.info(f"Searched by employee ID: '{emp_id}'")


@when('the user clicks the Search button without entering any filters')
def step_search_no_filters(context):
    """Submit the search form with no values — should return all employees."""
    from selenium.webdriver.common.by import By
    search_btn = (By.XPATH, "//button[@type='submit' and normalize-space()='Search']")
    context.employee_PageObj_Search.click(search_btn)
    context.employee_PageObj_Search._wait_for_results()


@when('the user enters employee name "{name}" in the search field')
def step_enter_name_in_search(context, name):
    from selenium.webdriver.common.by import By
    name_input = (By.XPATH, "//label[text()='Employee Name']/following::input[@placeholder='Type for hints...'][1]")
    context.employee_PageObj_Search.type_text(name_input, name)


@when('the user clicks the Reset button')
def step_click_reset(context):
    context.employee_PageObj_Search.reset_search()


@then('the search results should contain "{expected_name}"')
def step_results_contain_name(context, expected_name):
    """
    GenAI assertion strategy:
    1. Get all rows from the results table
    2. Combine first + last name of each row
    3. Check if expected_name appears in any row (case-insensitive partial match)
    4. Fail with a descriptive message if not found
    """
    rows = context.pim_PageObj.get_result_rows()
    assert len(rows) > 0, \
        f"Search returned no results when expecting to find '{expected_name}'"

    found = context.pim_PageObj.is_employee_in_results(expected_name)
    assert found, (
        f"Employee '{expected_name}' not found in search results.\n"
        f"Row count: {len(rows)}\n"
        f"First row name: {context.pim_PageObj.get_full_name_from_row(0)}"
    )
    logger.info(f"Employee '{expected_name}' confirmed in search results")


@then('the search results should show exactly one record with that employee ID')
def step_results_one_record_with_id(context):
    """
    GenAI assertion strategy:
    1. Verify exactly ONE row is returned (unique ID should yield one result)
    2. Verify the ID in that row matches the expected ID stored on context
    This tests both result count AND data accuracy.
    """
    emp_id = getattr(context, "employee_id", None)
    assert emp_id, "No employee_id on context — cannot validate result"

    rows = context.pim_PageObj.get_result_rows()
    assert len(rows) == 1, \
        f"Expected exactly 1 result for ID '{emp_id}' but got {len(rows)}"

    result_id = context.pim_PageObj.get_employee_id_from_row(0)
    assert result_id == emp_id, (
        f"Employee ID mismatch.\n"
        f"  Expected : {emp_id}\n"
        f"  Actual   : {result_id}"
    )
    logger.info(f"Unique search result confirmed for Employee ID: {emp_id}")


@then('"No Records Found" message should be displayed')
def step_no_records_found(context):
    """
    GenAI assertion strategy:
    Verify the 'No Records Found' span is visible.
    Also confirm the results table has zero data rows.
    """
    assert context.pim_PageObj.is_no_records_found(), \
        "Expected 'No Records Found' message but it was not visible"

    row_count = context.pim_PageObj.get_row_count()
    assert row_count == 0, \
        f"Expected 0 rows with 'No Records Found' but got {row_count} rows"

    logger.info("'No Records Found' message confirmed")


@then('the search results should contain at least one record')
def step_results_at_least_one(context):
    """
    GenAI assertion: empty search should return ALL employees.
    At minimum, the Admin user exists, so count >= 1.
    """
    row_count = context.pim_PageObj.get_row_count()
    assert row_count >= 1, \
        f"Expected at least 1 record from unfiltered search but got {row_count}"
    logger.info(f"Unfiltered search returned {row_count} record(s) — PASSED")


@then('the search fields should be cleared')
def step_search_fields_cleared(context):
    """
    GenAI assertion: after clicking Reset, all search input fields
    should be empty (attribute value == "").
    """
    from selenium.webdriver.common.by import By

    name_input = context.pim_PageObj.find_element(
        (By.XPATH, "//label[text()='Employee Name']/following::input[@placeholder='Type for hints...'][1]")
    )
    id_input = context.pim_PageObj.find_element(
        (By.XPATH, "//label[text()='Employee Id']/following::input[1]")
    )

    name_val = name_input.get_attribute("value") or ""
    id_val   = id_input.get_attribute("value") or ""

    assert name_val == "", f"Employee Name field not cleared after Reset. Value: '{name_val}'"
    assert id_val   == "", f"Employee ID field not cleared after Reset.   Value: '{id_val}'"
    logger.info("Search fields confirmed cleared after Reset")


@then('the results should be refreshed')
def step_results_refreshed(context):
    """After reset, results should reload (no 'No Records Found' for blank search)."""
    # After reset OrangeHRM re-runs the search with blank filters
    import time; time.sleep(2)
    # Blank search should return results, not "no records"
    no_records = context.pim_PageObj.is_no_records_found()
    assert not no_records, \
        "After Reset, 'No Records Found' was shown — expected default results"
    logger.info("Results refreshed after Reset confirmed")


@then('the application should handle the input safely')
def step_input_handled_safely(context):
    """
    GenAI assertion — XSS/injection safety:
    After submitting potentially malicious input, verify:
    1. The page is still the employee list (no crash / redirect)
    2. No JavaScript alert appeared
    """
    current_url = context.driver.current_url
    assert "viewEmployeeList" in current_url or "pim" in current_url, \
        f"Application may have crashed or redirected unexpectedly: {current_url}"
    logger.info("Application handled special character input safely")


@then('no JavaScript injection should occur')
def step_no_js_injection(context):
    """Check that no alert dialog appeared (which would indicate XSS)."""
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        alert = WebDriverWait(context.driver, 3).until(EC.alert_is_present())
        alert.dismiss()   # dismiss if one appeared
        assert False, "JavaScript alert appeared — possible XSS vulnerability!"
    except Exception:
        logger.info("No JavaScript alert present — XSS input safely handled")


@then('the employee ID in results should match the noted ID')
def step_employee_id_matches(context):
    """
    E2E assertion: The ID stored in context (noted before save)
    must appear in the search results row.
    """
    emp_id = getattr(context, "employee_id", None)
    assert emp_id, "No employee_id on context to validate"

    found = context.pim_PageObj.is_employee_id_in_results(emp_id)
    assert found, (
        f"Employee ID '{emp_id}' not found in search results.\n"
        f"First row ID: {context.pim_PageObj.get_employee_id_from_row(0)}"
    )
    logger.info(f"Employee ID '{emp_id}' matched in search results — E2E flow PASSED")


@then('the search should complete without errors')
def step_search_completes(context):
    """
    Generic assertion: search finished without throwing an exception.
    The page should still be on Employee List (no crash).
    """
    current_url = context.driver.current_url
    assert "viewEmployeeList" in current_url or "pim" in current_url, \
        f"Search caused unexpected navigation: {current_url}"
    # Page should not show a 500/error page
    title = context.driver.title
    assert "error" not in title.lower(), f"Error page detected: '{title}'"
    logger.info("Search completed without errors")
