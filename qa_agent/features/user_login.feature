Feature: User Login

  As a registered user
  I want to log in with my credentials
  So that I can access my dashboard

  Scenario: Successful login with valid credentials
    Given a registered user exists with username "valid_user" and password "valid_password"
    And the user is on the login page
    When the user enters username "valid_user" and password "valid_password"
    And the user submits the login credentials
    Then the user should be redirected to the dashboard
