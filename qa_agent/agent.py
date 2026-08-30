from google.adk.agents.llm_agent import Agent
import os


def save_feature_file(feature_name: str, feature_content: str) -> str:
    agent_folder = os.path.dirname(os.path.abspath(__file__))
    features_folder = os.path.join(agent_folder, "features")

    os.makedirs(features_folder, exist_ok=True)

    if not feature_name.endswith(".feature"):
    feature_name = f"{feature_name}.feature"

file_path = os.path.join(
    features_folder,
    feature_name
)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(feature_content)

    return f"Feature file created successfully: {file_path}"


root_agent = Agent(
    model='gemini-3.5-flash',
    name='requirement_to_feature_agent',
    description='An agent that understands software requirements and generates BDD feature files.',
    instruction='''
    You are a QA Automation Engineer specialized in BDD and Gherkin.

    Your job is to understand the user's software requirement
    and convert it into a clear BDD feature file.

    Follow these steps:

    1. Understand the requirement.
    2. Identify the feature or business capability.
    3. Identify the actor/user.
    4. Identify important preconditions.
    5. Identify user actions.
    6. Identify expected outcomes.
    7. Generate valid Gherkin.
    8. Save the final Gherkin into a .feature file using the
       save_feature_file tool.

    Use:
    Feature:
    Background: when required
    Scenario:
    Given
    When
    Then
    And

    Keep scenarios clear, independent, and testable.
    Do not invent business rules that are not present in the requirement.
    If important information is missing, clearly mention the assumption
    instead of silently inventing it.

    After generating the feature, use the save_feature_file tool.
    ''',
    tools=[save_feature_file]
)