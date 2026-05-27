# OrangeHRM Automation Framework
### Add & Search Employee — BDD Test Suite (Python + Selenium + Behave)

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Setup Instructions](#4-setup-instructions)
5. [Running Tests](#5-running-tests)
6. [Feature Files & Scenarios](#6-feature-files--scenarios)
7. [Page Object Model](#7-page-object-model)
8. [GenAI Integration Tasks](#8-genai-integration-tasks)
9. [Reporting](#9-reporting)
10. [CI/CD Pipeline](#10-cicd-pipeline)
11. [Docker Execution](#11-docker-execution)
12. [Data-Driven Testing](#12-data-driven-testing)
13. [Debugging Guide](#13-debugging-guide)
14. [Architecture Decisions](#14-architecture-decisions)

---

## 1. Project Overview

This framework automates the **Add Employee** and **Search Employee** workflows
on the [OrangeHRM Demo Site](https://opensource-demo.orangehrmlive.com) using:

- **BDD** (Behaviour-Driven Development) with Gherkin `.feature` files
- **Page Object Model** (POM) for maintainable, reusable UI interaction code
- **Data-driven testing** using CSV test data
- **Allure + HTML** reports with automatic screenshots on failure
- **GitHub Actions** CI/CD pipeline
- **Docker** for environment-independent execution

### Automated Workflows
| Workflow | Scenarios |
|---|---|
| Login | Valid login, invalid credentials, empty fields |
| Add Employee | Mandatory fields, all fields, custom ID, login toggle, validation errors |
| Search Employee | By name, by ID, by full name, no filters, reset, no results |
| End-to-End | Add → Search full flow |

---

## 2. Technology Stack

| Tool | Purpose | Version |
|---|---|---|
| Python | Language | 3.11+ |
| Selenium | Browser automation | 4.18 |
| Behave | BDD test runner (Gherkin) | 1.2.6 |
| webdriver-manager | Auto-downloads ChromeDriver | 4.0.1 |
| allure-behave | Allure report integration | 2.13.5 |
| behave-html-formatter | HTML report | 0.9.10 |
| python-dotenv | Environment config | 1.0.1 |
| colorlog | Coloured logging | 6.8.2 |
| Docker | Container execution | 24+ |
| GitHub Actions | CI/CD | — |

---

## 3. Project Structure

```
orangehrm-automation/
│
├── .env                          # Environment variables (browser, URLs, creds)
├── behave.ini                    # Behave runner configuration
├── requirements.txt              # Python dependencies
├── run_tests.sh                  # Convenience shell script
│
├── config/
│   ├── __init__.py
│   └── settings.py               # Typed settings loaded from .env
│
├── features/
│   ├── environment.py            # Behave hooks (before/after scenario, screenshots)
│   └── add_search_employee.feature  # ALL Gherkin scenarios
│
├── steps/
│   ├── __init__.py
│   ├── login_steps.py            # Login step definitions
│   ├── add_employee_steps.py     # Add Employee step definitions
│   └── search_employee_steps.py  # Search Employee step definitions
│
├── pages/
│   ├── __init__.py
│   ├── base_page.py              # Base Page Object (all shared Selenium actions)
│   ├── login_page.py             # Login page locators + actions
│   └── pim_page.py               # PIM module: AddEmployeePage + PIMPage
│
├── utils/
│   ├── __init__.py
│   ├── driver_factory.py         # WebDriver factory (Chrome/Firefox/Edge)
│   ├── helpers.py                # Screenshots, logger, wait helpers
│   └── data_reader.py            # CSV test data reader
│
├── data/
│   └── employee_data.csv         # Data-driven test input
│
├── reports/                      # HTML reports output (git-ignored)
├── screenshots/                  # PNG screenshots (git-ignored)
├── allure-results/               # Allure raw data (git-ignored)
│
├── docker/
│   ├── Dockerfile                # Container definition
│   └── docker-compose.yml        # Multi-service Docker setup
│
└── .github/
    └── workflows/
        └── automation.yml        # GitHub Actions CI/CD pipeline
```

---

## 4. Setup Instructions

### Prerequisites
- Python 3.11+
- Google Chrome (latest stable)
- Git

### Step 1 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/orangehrm-automation.git
cd orangehrm-automation
```

### Step 2 — Create and activate a virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```
> ChromeDriver is **automatically downloaded** by webdriver-manager on first run.

### Step 4 — Configure environment
```bash
cp .env .env.local       # optional: keep your local overrides
```
Edit `.env` to change browser, headless mode, or credentials:
```dotenv
BROWSER=chrome           # chrome | firefox | edge
HEADLESS=false           # true for CI / Docker
BASE_URL=https://opensource-demo.orangehrmlive.com
ADMIN_USERNAME=Admin
ADMIN_PASSWORD=admin123
```

---

## 5. Running Tests

### Run all tests
```bash
behave
```

### Run by tag
```bash
behave --tags @smoke          # fast sanity check (3 scenarios)
behave --tags @regression     # full suite
behave --tags @add            # only Add Employee scenarios
behave --tags @search         # only Search Employee scenarios
behave --tags @negative       # only negative/failure scenarios
behave --tags "@add and @positive"   # add + positive only
```

### Run with HTML report
```bash
behave --format behave_html_formatter:HTMLFormatter --outfile reports/report.html
```

### Run with Allure report
```bash
behave --format allure_behave.formatter:AllureFormatter --outfile allure-results
allure serve allure-results    # opens browser with interactive report
```

### Run using the shell script
```bash
chmod +x run_tests.sh
./run_tests.sh              # all tests
./run_tests.sh smoke        # @smoke only
./run_tests.sh regression   # @regression
```

### Run headless (no browser window)
```bash
HEADLESS=true behave --tags @smoke
```

---

## 6. Feature Files & Scenarios

### Tags Overview
| Tag | Purpose |
|---|---|
| `@smoke` | Critical happy-path, runs on every push (fast) |
| `@regression` | Full test suite |
| `@positive` | Expected-success scenarios |
| `@negative` | Expected-failure / error handling |
| `@add` | Add Employee workflow |
| `@search` | Search Employee workflow |
| `@login` | Authentication scenarios |
| `@data_driven` | Parameterised `Scenario Outline` |

### Scenario Count by Category
| Category | Count |
|---|---|
| Login | 5 |
| Add Employee — positive | 5 |
| Add Employee — negative | 5 |
| Search Employee — positive | 6 |
| Search Employee — negative | 3 |
| End-to-End | 1 |
| Data-Driven (Outline × examples) | 8 + 3 = 11 |
| **Total** | **36** |

---

## 7. Page Object Model

### Class Hierarchy
```
BasePage
  ├── LoginPage          ← /auth/login
  ├── PIMPage            ← /pim/viewEmployeeList (search)
  └── AddEmployeePage    ← /pim/addEmployee
```

### BasePage provides
- `find_element(locator)` — explicit wait + visibility check
- `click(locator)` — with JS-click fallback for intercepted clicks
- `type_text(locator, text)` — clear + send_keys
- `wait_for_url_contains(url)` — URL assertion helper
- `take_screenshot(name)` — saves PNG to screenshots/

### Locator Strategy
All locators use **stable, semantic XPath**:
```python
# Prefer label-relative XPath (resilient to layout changes)
EMPLOYEE_ID_INPUT = (By.XPATH, "//label[text()='Employee Id']/following::input[1]")

# Use button text rather than position
SAVE_BUTTON = (By.XPATH, "//button[@type='submit'][.//span[text()='Save']]")

# Use name attribute where available (most stable)
FIRST_NAME_INPUT = (By.NAME, "firstName")
```

---

## 8. GenAI Integration Tasks

### Task 1 — Feature File Generation
The entire `features/add_search_employee.feature` was generated by providing
this prompt to the AI:

> *"Generate a BDD Gherkin feature file for Add and Search Employee in OrangeHRM.
> Include positive, negative, and edge case scenarios. Use a Background for login.
> Apply tags: @smoke, @regression, @positive, @negative, @add, @search."*

### Task 2 — Locator Creation
Locators for all OrangeHRM PIM module elements were generated with:

> *"Generate Selenium locators for the OrangeHRM Add Employee form.
> Use stable XPath strategies. The page has: firstName (name attr),
> lastName (name attr), middleName (name attr), Employee ID (label-relative),
> Save button (submit with span text 'Save')."*

Key generated locators in `pages/pim_page.py`:
```python
SEARCH_EMPLOYEE_NAME = (By.XPATH,
    "//label[text()='Employee Name']/following::input[@placeholder='Type for hints...'][1]")
SAVE_BUTTON = (By.XPATH,
    "//button[@type='submit'][.//span[text()='Save']]")
TABLE_ROWS  = (By.XPATH,
    "//div[@class='oxd-table-body']//div[@role='row']")
```

### Task 3 — Assertion Writing
GenAI-written assertions in `steps/search_employee_steps.py`:

```python
@then('the search results should contain "{expected_name}"')
def step_results_contain_name(context, expected_name):
    """
    Strategy:
    1. Assert result table is not empty
    2. Iterate all rows, combine first+last name
    3. Case-insensitive partial match against expected_name
    4. Fail with descriptive message including actual row data
    """
    rows  = context.pim_page.get_result_rows()
    assert len(rows) > 0, f"No results when expecting '{expected_name}'"
    found = context.pim_page.is_employee_in_results(expected_name)
    assert found, f"'{expected_name}' not in results. Row 0: {context.pim_page.get_full_name_from_row(0)}"
```

### Task 4 — Debugging Help
**Q: Why is the script failing to locate the Save button?**

Common reasons and fixes:

| Root Cause | Symptom | Fix |
|---|---|---|
| Button inside iframe | `NoSuchElementException` | `driver.switch_to.frame(frame)` first |
| Page still loading | `ElementNotInteractableException` | Use `EC.element_to_be_clickable()` |
| Overlapping element | `ElementClickInterceptedException` | JS click fallback (already in BasePage) |
| Wrong XPath | `NoSuchElementException` | Inspect with DevTools → Copy XPath |
| Shadow DOM | `NoSuchElementException` | Use `execute_script` to pierce shadow root |
| Dynamic ID changed | Stale locator | Switch to text-based XPath |

Debugging snippet:
```python
# In browser console (F12):
# Find all buttons with their text:
document.querySelectorAll("button").forEach(b => console.log(b.textContent, b.type))

# In Python — dump page source when element not found:
with open("debug_page.html", "w") as f:
    f.write(driver.page_source)
```

### Task 5 — Report Setup
Reports are configured in `features/environment.py` and `behave.ini`.

Two report formats run simultaneously:
1. **Allure** — rich interactive HTML with steps, screenshots, timeline
2. **behave-html-formatter** — simple self-contained HTML file

---

## 9. Reporting

### HTML Report (behave-html-formatter)
```bash
behave --format behave_html_formatter:HTMLFormatter --outfile reports/report.html
open reports/report.html
```
Shows: scenario status, step details, duration, tags.

### Allure Report (interactive)
```bash
behave --format allure_behave.formatter:AllureFormatter --outfile allure-results
allure serve allure-results
```
Shows: test timeline, categories, environment, trends across runs, screenshots.

### Screenshot on Failure
Configured in `features/environment.py → after_step()`:
- Fires automatically when **any step fails**
- Saves to `screenshots/FAIL_<scenario>_<step>_<timestamp>.png`
- Attached to Allure report automatically

---

## 10. CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/automation.yml`)

**Triggers:**
- `push` to `main`/`develop` → runs `@smoke` only (< 5 min)
- `pull_request` → runs `@smoke + @regression`
- Nightly schedule (2 AM UTC) → full suite
- Manual `workflow_dispatch` → choose tags + browser

**Pipeline steps:**
1. Checkout code
2. Set up Python 3.11
3. Install Chrome + pip dependencies
4. Create output directories
5. Run Behave with selected tags
6. Upload HTML report as artifact (30 days)
7. Upload screenshots (7 days)
8. Generate and publish Allure report to GitHub Pages
9. Notify on failure (Slack webhook ready)

---

## 11. Docker Execution

### Build and run
```bash
cd docker/
docker-compose build
docker-compose up tests
```

### Run specific tags
```bash
docker run orangehrm-tests behave --tags @smoke --headless=true
```

### View reports after run
```bash
# Reports are volume-mounted to the host:
open reports/report.html
allure serve allure-results
```

### Architecture
```
docker-compose up
  ├── tests container   → headless Chrome + Behave
  ├── selenium-hub      → Selenium Grid 4 hub
  └── chrome-node       → Chrome node registered to hub
```

---

## 12. Data-Driven Testing

### Scenario Outline (inline)
In the feature file, multiple employees are tested using `Examples:` tables:
```gherkin
Scenario Outline: Add multiple employees
  When the user enters first name "<first_name>" and last name "<last_name>"
  Examples:
    | first_name | last_name  |
    | DataUser01 | TestLast01 |
    | DataUser02 | TestLast02 |
```

### External CSV Data (`data/employee_data.csv`)
```python
from utils.data_reader import get_valid_employees

employees = get_valid_employees()
for emp in employees:
    # Use emp['first_name'], emp['last_name'], etc.
```

---

## 13. Debugging Guide

### Common Issues

**1. ChromeDriver version mismatch**
```
SessionNotCreatedException: session not created: Chrome version must be ...
```
Fix: `pip install --upgrade webdriver-manager` — it auto-downloads the right driver.

**2. Element not found (timeout)**
```
TimeoutException: Message: element not visible after 30 seconds
```
Debug steps:
- Increase `EXPLICIT_WAIT` in `.env`
- Check if element is inside an iframe: `driver.switch_to.frame(...)`
- Dump page source: `open("debug.html", "w").write(driver.page_source)`
- Check OrangeHRM spinner hasn't stalled: add `time.sleep(2)` before the find

**3. Stale element reference**
```
StaleElementReferenceException
```
Fix: Re-find the element after any page action. Never store element references across steps.

**4. Tests pass locally but fail in CI**
- Ensure `HEADLESS=true` in CI environment
- Add `--no-sandbox --disable-dev-shm-usage` Chrome flags (already in DriverFactory)
- Check if demo site has rate limiting

---

## 14. Architecture Decisions

| Decision | Rationale |
|---|---|
| **Behave (BDD)** | Non-technical stakeholders can read `.feature` files |
| **Page Object Model** | Locators centralised — one change updates all tests |
| **environment.py hooks** | Screenshots captured automatically at failure point |
| **webdriver-manager** | No manual ChromeDriver downloads or version management |
| **.env + settings.py** | Single place to change browser/URL without touching test code |
| **Explicit waits everywhere** | More reliable than `time.sleep()` across different machines |
| **JS click fallback** | Handles OrangeHRM's overlay elements gracefully |
| **Allure + HTML dual report** | Allure for developers (rich), HTML for stakeholders (simple) |