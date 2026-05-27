Feature: Login Functionality

Background: 
  Given the user navigates to the OrangeHRM login page

@smoke @login
Scenario: Successful login with valid credentials
  When the user enters correct credentials
  And the user clicks the Login button
  Then the user should be redirected to the Dashboard page
  And the Dashboard header should be visible

@smoke @login @negative
Scenario: Login fails with invalid credentials
  When the user enters incorrect credentials
  And the user clicks the Login button
  Then an error message "Invalid credentials" should be displayed
  And the user should remain on the login page

@smoke @login @negative @try
Scenario: Login fails with empty credentials
  When the user submits the login form with empty credentials
  Then required field validation errors should be displayed