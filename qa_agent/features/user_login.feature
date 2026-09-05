Feature: User Login
  As a registered user
  I want to log in with my valid credentials
  So that I can access my personalized dashboard

  Scenario: Successful login with valid credentials
    Given the user is a registered user
    And the user is on the login page
    When the user enters a valid username and password
    And clicks the login button
    Then the user should be redirected to the dashboard
    And should see the dashboard page