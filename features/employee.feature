Feature: Employee Management

Background:
  Given the user is logged into the OrangeHRM application

#Add Employee
@regression @smoke @add
Scenario: Add a new employee with mandatory fields only
  Given the user is on the Add Employee page
  Then the Employee ID field should contain an auto-generated value
  When the user enters first name "L1" and last name "Track"
  And the user clicks the Save button
  Then the employee profile page should be displayed

@regression @add
Scenario: Add employee with full name and Specific employee ID with login Credentials
  Given the user is on the Add Employee page
  When the user enters first name "L1" and middle name "Automation" and last name "Track"
  And the user sets the employee ID to "L145"
  And the user enables the "Create Login Details" toggle
  And the user enters login username "L1_test" and password "Assignment@1234"
  And the user clicks the Save button
  Then the employee profile page should be displayed

@regression @add @data_driven
Scenario Outline: Add multiple employees using data table
  Given the user is on the Add Employee page
  When the user enters first name "<first_name>" and last name "<last_name>"
  And the user clicks the Save button
  Then the employee profile page should be displayed

  Examples:
    | first_name  | last_name   |
    | DataUser01  | TestLast01  |
    | DataUser02  | TestLast02  |
    | DataUser03  | TestLast03  |
    | DataUser04  | TestLast04  |
    | DataUser05  | TestLast05  |

@regression @smoke @search
Scenario: Search employee by first name returns results
  Given a new employee "FullNameFirst FullNameLast" has been added to the system
  When the user clicks the Save button
  And the user navigates to the Employee List page
  And the user searches for employee name "FullNameFirst"
  Then the search results should contain "FullNameFirst FullNameLast"

@regression @search
Scenario: Search employee by employee ID returns correct record
  Given a new employee with a known employee ID exists in the system
  When the user clicks the Save button
  And the user navigates to the Employee List page
  And the user searches by the employee ID
  Then the search results should show exactly one record with that employee ID

@regression @search
Scenario: Search employee by last name returns results
  Given a new employee "FullNameFirst FullNameLast" has been added to the system
  When the user clicks the Save button
  And the user navigates to the Employee List page
  And the user searches for employee name "FullNameLast"
  Then the search results should contain "FullNameFirst FullNameLast"

@regression @search
Scenario: Search employee by full name returns exact match
  Given a new employee "FullNameFirst FullNameLast" has been added to the system
  When the user clicks the Save button
  And the user navigates to the Employee List page
  And the user searches for employee name "FullNameFirst FullNameLast"
  Then the search results should contain "FullNameFirst FullNameLast"

@regression @search
Scenario: Search with no filters returns all employees
  Given the user is on the Employee List page
  When the user clicks the Search button without entering any filters
  Then the search results should contain at least one record

@regression @add @negativeadd
Scenario: Add employee fails without first name
  Given the user is on the Add Employee page
  When the user enters only last name "LastName"
  And the user clicks the Save button
  Then a required field validation error should appear for first name

@regression @add @negativeadd
Scenario: Add employee fails without last name
  Given the user is on the Add Employee page
  When the user enters only first name "FirstName"
  And the user clicks the Save button
  Then a required field validation error should appear for last name

@regression @add @negativeadd
Scenario: Add employee fails with no data entered
  Given the user is on the Add Employee page
  When the user clicks the Save button without entering any data
  Then multiple required field validation errors should be displayed

@regression @search @negativesearch
Scenario: Search with non-existent employee name returns no records
  Given the user is on the Employee List page
  When the user searches for employee name "XYZNONEXISTENT999"
  Then "No Records Found" message should be displayed

@regression @search @negativesearch
Scenario: Search with non-existent employee ID returns no records
  Given the user is on the Employee List page
  When the user searches by employee ID "INVALID999"
  Then "No Records Found" message should be displayed

@regression @search @negativesearch
Scenario: Search with special characters returns no records
  Given the user is on the Employee List page
  When the user searches for employee name "<script>alert('xss')</script>"
  Then the application should handle the input safely
  And no JavaScript injection should occur