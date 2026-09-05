@KAN-4
Feature: Create a New Task on Kanban Board
  As a project team member
  I want to create a new task on the Kanban board
  So that I can track work items and collaborate with my team effectively.

  Background:
    Given the user is logged into the Kanban application
    And the user is on the project board for project "KAN"

  Scenario: Successfully create a new task with required fields
    Given the user opens the "Create Task" dialog
    When the user enters the summary "Implement user authentication"
    And the user selects the issue type "Task"
    And the user clicks the "Create" button
    Then the task "Implement user authentication" should be created successfully
    And the task should appear in the "To Do" column on the Kanban board

  Scenario: Attempt to create a task without a mandatory summary
    Given the user opens the "Create Task" dialog
    When the user leaves the summary field empty
    And the user clicks the "Create" button
    Then an error message "Summary is required" should be displayed
    And the task creation form should remain open

  Scenario Outline: Create tasks with different priorities
    Given the user opens the "Create Task" dialog
    When the user enters the summary "<summary>"
    And the user selects priority "<priority>"
    And the user clicks the "Create" button
    Then the task "<summary>" should be created with priority "<priority>"

    Examples:
      | summary                  | priority |
      | Fix critical memory leak | Highest  |
      | Update documentation     | Low      |
