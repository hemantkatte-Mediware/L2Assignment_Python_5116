import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage
from config.settings import settings
from utils.helpers import get_logger

logger = get_logger(__name__)

class PIMPage(BasePage):
    """
    Handles the Employee List page and search functionality.
    URL: /web/index.php/pim/viewEmployeeList
    """

    PIM_URL = f"{settings.BASE_URL}/web/index.php/pim/viewEmployeeList"

    # ── Navigation sidebar ────────────────────────────────────────────────────
    PIM_MENU_ITEM           = (By.XPATH, "//span[text()='PIM']")
    EMPLOYEE_LIST_MENU_ITEM = (By.XPATH, "//a[text()='Employee List']")
    ADD_EMPLOYEE_BTN        = (By.XPATH, "//a[text()='Add Employee']")
    EMPLOYEE_LIST_BTN       = (By.XPATH, "//a[text()='Employee List']")

    # ── Search filters (Employee List page) ───────────────────────────────────
    SEARCH_EMPLOYEE_NAME  = (By.XPATH, "//label[text()='Employee Name']/following::input[@placeholder='Type for hints...'][1]")
    SEARCH_EMPLOYEE_ID    = (By.XPATH, "//label[text()='Employee Id']/following::input[1]")
    SEARCH_BUTTON         = (By.XPATH, "//button[@type='submit' and normalize-space()='Search']")
    RESET_BUTTON          = (By.XPATH, "//button[@type='submit' and normalize-space()='Reset']")

    # ── Results table ─────────────────────────────────────────────────────────
    RESULTS_TABLE          = (By.XPATH, "//div[@class='oxd-table']")
    TABLE_ROWS             = (By.XPATH, "//div[@class='oxd-table-body']//div[@role='row']")
    NO_RECORDS_FOUND       = (By.XPATH, "//span[text()='No Records Found']")
    RECORDS_FOUND_LABEL    = (By.XPATH, "//span[contains(@class,'oxd-text') and contains(text(),'Record')]")

    # ── Row data cells ────────────────────────────────────────────────────────
    # Each row has 6 cells: checkbox | ID | First | Middle | Last | Actions
    ROW_EMPLOYEE_ID    = ".//div[@role='cell'][2]/div"   # relative XPath inside a row
    ROW_FIRST_NAME     = ".//div[@role='cell'][3]/div" 
    ROW_LAST_NAME      = ".//div[@role='cell'][4]/div" 
    ROW_JOB_TITLE      = ".//div[@role='cell'][5]/div" 
    ROW_EDIT_BUTTON    = ".//button[@title='Edit']"

    # ── Actions ───────────────────────────────────────────────────────────────

    def navigate_to_pim(self):
        # 1. Open the direct PIM module URL
        self.open(self.PIM_URL)
    
        # 2. Add an explicit wait to let the search input load completely
        # (Assuming your base page 'find_element' includes an explicit visibility wait)
        try:
            self.find_element(self.SEARCH_EMPLOYEE_NAME)
            logger.info("PIM Employee List page loaded directly via URL.")
        except Exception:
        # 3. Fallback: If URL navigation didn't land on the list, click the tab item once
            logger.warning("Search field not immediately visible. Attempting recovery via menu click.")
            self.click(self.EMPLOYEE_LIST_MENU_ITEM)
            self.find_element(self.SEARCH_EMPLOYEE_NAME)
            logger.info("PIM Employee List page loaded via fallback menu click.")

    def navigate_via_menu(self):
        """Click PIM in the left sidebar navigation."""
        self.click(self.PIM_MENU_ITEM)
        self.find_element(self.SEARCH_EMPLOYEE_NAME)

    def go_to_add_employee(self):
        self.click(self.ADD_EMPLOYEE_BTN)
        logger.info("Navigated to Add Employee page")

    def search_by_name(self, name: str):
        """Type employee name in search box and submit."""
        self.type_text(self.SEARCH_EMPLOYEE_NAME, name)
        time.sleep(1)   # allow autocomplete suggestions to clear
        self.click(self.SEARCH_BUTTON)
        self._wait_for_results()

    def search_by_employee_id(self, emp_id: str):
        """Search using Employee ID field."""
        self.type_text(self.SEARCH_EMPLOYEE_ID, emp_id)
        self.click(self.SEARCH_BUTTON)
        self._wait_for_results()

    def search_by_name_and_id(self, name: str, emp_id: str):
        """Search using both name AND employee ID."""
        self.type_text(self.SEARCH_EMPLOYEE_NAME, name)
        time.sleep(1)
        self.type_text(self.SEARCH_EMPLOYEE_ID, emp_id)
        self.click(self.SEARCH_BUTTON)
        self._wait_for_results()

    def reset_search(self):
        self.click(self.RESET_BUTTON)

    def _wait_for_results(self):
        """Wait until the spinner disappears and results are shown."""
        time.sleep(2)   # OrangeHRM has a loading animation
        # Wait for either a result row OR "No Records Found"
        WebDriverWait(self.driver, settings.EXPLICIT_WAIT).until(
            lambda d: (
                self.is_element_visible(self.TABLE_ROWS,        timeout=2) or
                self.is_element_visible(self.NO_RECORDS_FOUND,  timeout=2)
            )
        )

    # ── Assertions / Getters ──────────────────────────────────────────────────

    def get_result_rows(self) -> list:
        if self.is_element_visible(self.NO_RECORDS_FOUND, timeout=3):
            return []
        return self.find_elements(self.TABLE_ROWS)

    def get_row_count(self) -> int:
        return len(self.get_result_rows())

    def is_no_records_found(self) -> bool:
        return self.is_element_visible(self.NO_RECORDS_FOUND, timeout=5)

    def get_employee_id_from_row(self, row_index: int = 0) -> str:
        rows = self.get_result_rows()
        if not rows or row_index >= len(rows):
            return ""
        cell = rows[row_index].find_element(By.XPATH, self.ROW_EMPLOYEE_ID)
        return cell.text.strip()

    def get_full_name_from_row(self, row_index: int = 0) -> str:
        rows = self.get_result_rows()
        if not rows or row_index >= len(rows):
            return ""
        first = rows[row_index].find_element(By.XPATH, self.ROW_FIRST_NAME).text.strip()
        last  = rows[row_index].find_element(By.XPATH, self.ROW_LAST_NAME).text.strip()
        return f"{first} {last}"

    def is_employee_in_results(self, name: str) -> bool:
        rows = self.get_result_rows()
        for row in rows:
            first = row.find_element(By.XPATH, self.ROW_FIRST_NAME).text.strip()
            last  = row.find_element(By.XPATH, self.ROW_LAST_NAME).text.strip()
            if name.lower() in f"{first} {last}".lower():
                return True
        return False

    def is_employee_id_in_results(self, emp_id: str) -> bool:
        rows = self.get_result_rows()
        for row in rows:
            cell_id = row.find_element(By.XPATH, self.ROW_EMPLOYEE_ID).text.strip()
            if emp_id == cell_id:
                return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Add Employee Page
# ─────────────────────────────────────────────────────────────────────────────

class AddEmployeePage(BasePage):
    """
    Handles the Add Employee form.
    URL: /web/index.php/pim/addEmployee
    """

    ADD_URL = f"{settings.BASE_URL}/web/index.php/pim/addEmployee"

    # ── Form fields ───────────────────────────────────────────────────────────
    FIRST_NAME_INPUT   = (By.NAME,  "firstName")
    MIDDLE_NAME_INPUT  = (By.NAME,  "middleName")
    LAST_NAME_INPUT    = (By.NAME,  "lastName")

    # Employee ID is auto-generated but can be overridden
    EMPLOYEE_ID_INPUT  = (By.XPATH, "//label[text()='Employee Id']/following::input[1]")

    # Toggle to create login details
    CREATE_LOGIN_TOGGLE = (By.XPATH, "//p[text()='Create Login Details']/following-sibling::div//span[contains(@class, 'oxd-switch-input')]")
    CREATE_LOGIN_STATUS = (By.XPATH, "//p[text()='Create Login Details']/following-sibling::div//input[@type='checkbox']")

    USERNAME_INPUT     = (By.XPATH, "//label[text()='Username']/following::input[1]")
    PASSWORD_INPUT     = (By.XPATH, "//label[text()='Password']/following::input[@type='password'][1]")
    CONFIRM_PASSWORD   = (By.XPATH, "//label[text()='Confirm Password']/following::input[@type='password'][1]")

    # ── Buttons ───────────────────────────────────────────────────────────────
    SAVE_BUTTON        = (By.XPATH, "//button[@type='submit' and normalize-space()='Save']")
    CANCEL_BUTTON      = (By.XPATH, "//button[@type='submit' and normalize-space()='Cancel']")

    # ── Profile picture ───────────────────────────────────────────────────────
    UPLOAD_PHOTO_BTN   = (By.XPATH, "//button[contains(@class,'employee-image-action')]")

    # ── Validation errors ─────────────────────────────────────────────────────
    FIELD_ERROR        = (By.XPATH, "//span[@class='oxd-input-field-error-message oxd-text--span']")
    ALL_FIELD_ERRORS   = (By.XPATH, "//span[contains(@class,'oxd-input-field-error-message')]")

    # ── Success / page after save ─────────────────────────────────────────────
    # After a successful save, OrangeHRM redirects to the employee profile edit page.
    EMPLOYEE_PROFILE_HEADER = (By.XPATH, "//h6[contains(@class,'oxd-text') and text()='Personal Details']")

    # ── Actions ───────────────────────────────────────────────────────────────

    def navigate(self):
        self.open(self.ADD_URL)
        self.find_element(self.FIRST_NAME_INPUT)
        logger.info("Add Employee page loaded")

    def enter_first_name(self, first_name: str):
        self.type_text(self.FIRST_NAME_INPUT, first_name)

    def enter_middle_name(self, middle_name: str):
        self.type_text(self.MIDDLE_NAME_INPUT, middle_name)

    def enter_last_name(self, last_name: str):
        self.type_text(self.LAST_NAME_INPUT, last_name)

    def get_employee_id(self) -> str:
        """Read the auto-generated Employee ID."""
        return self.get_attribute(self.EMPLOYEE_ID_INPUT, "value")

    def set_employee_id(self, emp_id: str):
        """Override the auto-generated ID with a specific value."""
        self.type_text(self.EMPLOYEE_ID_INPUT, emp_id)

    def enable_create_login(self):
        SPINNER_OVERLAY = (By.CLASS_NAME, "oxd-form-loader")
        self.wait.until(EC.invisibility_of_element_located(SPINNER_OVERLAY))
        # 1. Wait for presence (not visibility) to check if already enabled
        checkbox = self.wait.until(EC.presence_of_element_located(self.CREATE_LOGIN_STATUS))
        is_enabled = checkbox.is_selected()
    
        # 2. Click the visible span element only if it's currently turned off
        if not is_enabled:
            toggle = self.wait.until(EC.element_to_be_clickable(self.CREATE_LOGIN_TOGGLE))
            toggle.click()

    def enter_login_username(self, username: str):
        self.type_text(self.USERNAME_INPUT, username)

    def enter_login_password(self, password: str):
        self.type_text(self.PASSWORD_INPUT, password)

    def enter_confirm_password(self, password: str):
        self.type_text(self.CONFIRM_PASSWORD, password)

    def click_save(self):
        SPINNER_OVERLAY = (By.CLASS_NAME, "oxd-form-loader")
        try:
            WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located(SPINNER_OVERLAY))
        except Exception:
            pass
        self.wait.until(EC.element_to_be_clickable(self.SAVE_BUTTON))
        self.click(self.SAVE_BUTTON)
        logger.info("Save button clicked")

    def click_cancel(self):
        self.click(self.CANCEL_BUTTON)

    def fill_employee_form(
        self,
        first_name:   str,
        last_name:    str,
        middle_name:  str = "",
        employee_id:  str = None
    ) -> str:
        """
        Fills only the mandatory fields.
        Returns the Employee ID (auto-generated or set).
        """
        self.enter_first_name(first_name)
        if middle_name:
            self.enter_middle_name(middle_name)
        self.enter_last_name(last_name)

        if employee_id:
            self.set_employee_id(employee_id)

        # Read the ID AFTER potentially setting it
        generated_id = self.get_employee_id()
        logger.info(f"Employee form filled: {first_name} {last_name} | ID: {generated_id}")
        return generated_id

    # def save_and_wait(self):
    #     """Click save and wait for the redirect to Personal Details."""
    #     self.click_save()
    #     # OrangeHRM redirects to the employee profile on success
    #     try:
    #         self.wait_for_url_contains("viewPersonalDetails")
    #     except Exception:
    #         # Some versions redirect differently — check for profile header
    #         self.find_element(self.EMPLOYEE_PROFILE_HEADER)
    
    def save_and_wait(self, timeout=30):
        """Click save and wait for the profile page to load."""
        self.click_save()
        
        # 1. Look for a quick validation error (e.g., 'Employee Id already exists')
        VALIDATION_ERROR = (By.XPATH, "//span[contains(@class, 'oxd-input-field-error-message')]")
        
        try:
            error_element = self.find_element(VALIDATION_ERROR)
            if error_element and error_element.is_displayed():
                raise AssertionError(f"Form submission failed with validation error: {error_element.text}")
        except Exception:
            pass

        # 2. Wait for successful navigation or component visibility
        try:
            # REMOVED the timeout keyword argument here to match your BasePage signature
            self.wait_for_url_contains("viewPersonalDetails")
        except Exception:
            # Final fallback check in case the URL pattern changed but page loaded
            try:
                self.find_element(self.EMPLOYEE_PROFILE_HEADER)
            except Exception:
                raise TimeoutException(
                    f"Application failed to save employee and redirect within {timeout} seconds. "
                    "Check application responsiveness or for unhandled UI error popups."
                )

    # ── Assertions / State Checks ─────────────────────────────────────────────

    def get_validation_errors(self) -> list:
        """Returns a list of all visible validation error messages."""
        if not self.is_element_visible(self.ALL_FIELD_ERRORS, timeout=5):
            return []
        elements = self.find_elements(self.ALL_FIELD_ERRORS)
        return [e.text.strip() for e in elements if e.text.strip()]

    def is_on_add_employee_page(self) -> bool:
        return "addEmployee" in self.get_current_url()

    def is_save_successful(self) -> bool:
        """True if the page redirected to employee profile after save."""
        return "viewPersonalDetails" in self.get_current_url()
    
