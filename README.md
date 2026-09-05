# 🤖 Google ADK QA Automation Agent

An AI-powered QA Automation Agent built using **Google Agent Development Kit (ADK)**, **Python**, and **Gemini**.

The current version focuses on converting a natural-language software requirement into a **BDD/Gherkin feature file**.

---

## 🎯 Project Goal

The goal of this project is to explore how AI Agents can assist QA Automation Engineers by automating repetitive activities in the software testing lifecycle.

### Current Capability

The agent accepts a natural-language requirement and:

1. Understands the requirement
2. Identifies the business capability
3. Identifies the actor/user
4. Identifies preconditions
5. Identifies user actions
6. Identifies expected outcomes
7. Generates BDD/Gherkin scenarios
8. Automatically creates a `.feature` file

### Current Flow

```text
                 User Requirement
                        │
                        ▼
              Google ADK QA Agent
                        │
                        ▼
               Requirement Analysis
                        │
                        ▼
                 Gherkin Generation
                        │
                        ▼
                save_feature_file()
                        │
                        ▼
                  .feature File
```

---

## 🛠️ Technology Stack

- Python
- Google Agent Development Kit (ADK)
- Gemini
- BDD
- Gherkin
- Git
- GitHub

---

## 📁 Project Structure

```text
Google_ADK_Agent_Practice/
│
├── .gitignore
├── .venv/
│   └── Virtual Python Environment
│
├── evals/
│   ├── coverage_evaluator.py
│   ├── eval_config.json
│   ├── eval_metrics.py
│   ├── qa_gate.py
│   ├── requirement_to_feature.evalset.json
│   │
│   └── requirements/
│       ├── base.py
│       ├── jira_adapter.py
│       ├── models.py
│       ├── pdf_adapter.py
│       │
│       └── tests/
│           ├── test_jira_adapter.py
│           └── test_pdf_adapter.py
│
└── qa_agent/
    ├── .env
    ├── .gitignore
    ├── __init__.py
    ├── agent.py
    ├── eval_metrics.py
    │
    └── features/
        ├── user_login.feature
        └── KAN-4_create_task.feature
```

### File and Folder Description

| File / Folder | Purpose |
|---|---|
| `.venv/` | Python virtual environment |
| `.gitignore` | Prevents secrets and unnecessary files from being committed |
| `qa_agent/` | Main ADK agent package |
| `agent.py` | Agent definition and custom Python tool |
| `__init__.py` | Python package initialization |
| `.env` | Stores Google and Jira API credentials locally |
| `features/` | Stores generated Gherkin feature files |
| `user_login.feature` | Example BDD feature file |
| `KAN-4_create_task.feature` | BDD feature generated from Jira ticket KAN-4 |
| `evals/` | Contains evaluation and requirement-source components |
| `coverage_evaluator.py` | Evaluates requirement-to-feature coverage |
| `eval_config.json` | Evaluation configuration |
| `eval_metrics.py` | Evaluation metrics |
| `qa_gate.py` | Final QA gate decision |
| `requirement_to_feature.evalset.json` | ADK evaluation test data |
| `requirements/base.py` | Defines the common requirement-source contract |
| `requirements/models.py` | Defines requirement data models |
| `requirements/jira_adapter.py` | Fetches and converts Jira requirements |
| `requirements/pdf_adapter.py` | Fetches and converts PDF requirements |
| `requirements/tests/` | Tests for requirement adapters |

---

# ⚙️ Prerequisites

Before starting, make sure you have:

- Windows / macOS / Linux
- Python 3.x
- VS Code
- Git
- Google account
- Google AI API key
- Jira account/API credentials if using the Jira adapter

---

# 🐍 Step 1 — Install Python

Download Python from:

https://www.python.org/downloads/

During Windows installation, make sure to select:

```text
☑ Add python.exe to PATH
```

---

# 📂 Step 2 — Create the Project Folder

Create:

```text
Google_ADK_Agent_Practice
```

Open the folder in VS Code.

---

# 🧪 Step 3 — Create a Python Virtual Environment

Open the VS Code terminal:

```powershell
python -m venv .venv
```

This creates:

```text
.venv/
```

The virtual environment keeps project dependencies isolated from the system Python installation.

---

# ▶️ Step 4 — Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal should show something similar to:

```text
(.venv) PS D:\Automation_Practice_2026\Google_ADK_Agent_Practice>
```

---

# 📦 Step 5 — Install Google ADK

Install Google Agent Development Kit:

```powershell
pip install google-adk
```

Verify:

```powershell
pip show google-adk
```

---

# 🤖 Step 6 — Create the ADK Agent

From the project root:

```powershell
adk create qa_agent
```

If `adk` is not recognized in PowerShell, use the virtual-environment executable directly:

```powershell
.\.venv\Scripts\adk.exe create qa_agent
```

---

# 📦 Step 7 — Install Additional Dependencies

The requirement adapters use additional Python packages.

Install:

```powershell
pip install python-dotenv requests pymupdf
```

For pytest:

```powershell
pip install pytest
```

---

# 🔑 Step 8 — Configure Google API Key

The agent requires a Google API key.

Create an API key using Google AI Studio:

https://aistudio.google.com/apikey

Create:

```text
qa_agent/.env
```

Add:

```env
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
```

Example:

```env
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXX
```

**Do not commit `.env` to GitHub.**

---

# 🔑 Step 9 — Configure Jira API Credentials

For the Jira requirement adapter, configure:

```env
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=YOUR_JIRA_API_TOKEN
```

The Jira adapter uses these values to authenticate against Jira and retrieve a ticket such as:

```text
KAN-4
```

The Jira ticket is converted into the common `Requirement` model before being passed downstream.

---

# 🧠 Step 10 — Requirement Source Architecture

The project supports multiple requirement sources.

The basic architecture is:

```text
             Requirement Source
                     │
          ┌──────────┼──────────┐
          │          │          │
         Jira       PDF      Future Source
          │          │          │
          └──────────┼──────────┘
                     │
                     ▼
                Requirement
                     │
                     ▼
              QA Agent / Evals
                     │
                     ▼
              BDD Feature File
```

The common contract is defined in:

```text
evals/requirements/base.py
```

The `RequirementSourceAdapter` protocol defines:

```python
fetch(locator: str) -> Requirement
```

This allows Jira, PDF, Confluence, Word, or another future source to provide requirements in a common format.

---

# 🧾 Step 11 — Jira Adapter

The Jira adapter is located at:

```text
evals/requirements/jira_adapter.py
```

Its responsibility is to:

1. Connect to Jira
2. Fetch a Jira issue
3. Read the issue description
4. Convert Jira's Atlassian Document Format (ADF) into plain text
5. Extract acceptance criteria
6. Process supported attachments
7. Return a `Requirement` object

Example:

```text
Jira
 │
 │ KAN-4
 ▼
JiraAdapter
 │
 ├── Description
 ├── Acceptance Criteria
 └── Attachments
       │
       ├── Image
       └── PDF
 │
 ▼
Requirement
```

If an image or PDF is attached to the Jira ticket, the adapter can retrieve supported attachments and use the Gemini vision-capable model to describe them.

---

# 📄 Step 12 — PDF Adapter

The PDF adapter is located at:

```text
evals/requirements/pdf_adapter.py
```

It supports PDF requirements.

The adapter first attempts to extract text directly from the PDF.

For scanned/image-only pages, it can fall back to rasterization and vision-model processing.

Example:

```text
PDF
 │
 ├── Text layer
 │       │
 │       ▼
 │    Extract text
 │
 └── Scanned page
         │
         ▼
      Render image
         │
         ▼
      Gemini Vision
         │
         ▼
     Requirement
```

---

# 🧪 Step 13 — Requirement Adapter Tests

Tests are located under:

```text
evals/requirements/tests/
```

Jira:

```text
test_jira_adapter.py
```

PDF:

```text
test_pdf_adapter.py
```

Run Jira adapter tests:

```powershell
python -m pytest evals/requirements/tests/test_jira_adapter.py -v -s
```

Run PDF adapter tests:

```powershell
python -m pytest evals/requirements/tests/test_pdf_adapter.py -v -s
```

Run all requirement tests:

```powershell
python -m pytest evals/requirements/tests -v -s
```

These tests verify the **Python requirement adapters themselves**.

They are separate from the ADK evaluation.

---

# 🧠 Step 14 — Agent Implementation

The main agent is located at:

```text
qa_agent/agent.py
```

The agent is configured to understand requirements and generate BDD/Gherkin feature files.

Example implementation:

```python
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
    model="gemini-3.5-flash",
    name="requirement_to_feature_agent",
    description=(
        "An agent that understands software requirements "
        "and generates BDD feature files."
    ),
    instruction="""
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
    """,
    tools=[save_feature_file]
)
```

---

# ▶️ Step 15 — Run the ADK Agent

From the project root:

```powershell
.\.venv\Scripts\adk.exe run .\qa_agent
```

The ADK CLI starts the agent.

Example:

```text
Running agent requirement_to_feature_agent, type exit to exit.
```

Then provide:

```text
Create a BDD feature file for Jira ticket KAN-4
```

The agent generates the feature file under:

```text
qa_agent/features/
```

---

# 🌐 Step 16 — ADK Web

You can also run the agent using the ADK web interface.

From the project root:

```powershell
.\.venv\Scripts\adk.exe web .\qa_agent
```

The ADK web interface allows you to interact with the agent through the browser.

---

# 📝 Step 17 — Example Jira Ticket

Example Jira ticket:

```text
KAN-4
```

The Jira adapter retrieves the ticket using:

```text
JIRA_BASE_URL
JIRA_EMAIL
JIRA_API_TOKEN
```

The resulting requirement contains:

```text
ID
Source
Title
Narrative
Acceptance Criteria
Evidence
Source Version
```

The requirement can then be used by the agent to generate the corresponding BDD feature.

---

# 🥒 Step 18 — Generated Feature File

Example generated file:

```text
qa_agent/features/KAN-4_create_task.feature
```

Example structure:

```gherkin
@KAN-4
Feature: Create a New Task on Kanban Board

  Scenario: Successfully create a new task
    Given ...
    When ...
    Then ...
```

The Jira ticket ID is retained through the feature tag:

```gherkin
@KAN-4
```

This provides traceability between:

```text
Jira Ticket
     │
     ▼
Requirement
     │
     ▼
BDD Feature
     │
     ▼
Automation
```

---

# 🧪 Step 19 — Custom EVAL

The project also contains custom evaluation components under:

```text
evals/
```

The custom evaluation can validate requirement-to-feature coverage and quality.

Example:

```text
Requirement
    │
    ▼
Generated Feature
    │
    ▼
coverage_evaluator.py
    │
    ▼
Evaluation Metrics
```

Run the custom evaluation according to the project's configured evaluation flow.

---

# 🧪 Step 20 — ADK EVAL

The ADK evaluation test set is:

```text
evals/requirement_to_feature.evalset.json
```

The evaluation configuration is:

```text
evals/eval_config.json
```

The purpose of ADK EVAL is to evaluate the behavior/output of the Google ADK agent against defined evaluation cases.

---

# 🚦 Step 21 — Final QA Gate

The final QA gate is implemented in:

```text
evals/qa_gate.py
```

Conceptually:

```text
Custom EVAL
     │
     ▼
ADK EVAL
     │
     ▼
Final QA Gate
     │
     ├── PASS
     │
     └── FAIL
```

The final gate determines whether the generated feature is acceptable for the next stage of the automation workflow.

---

# 🧪 Pytest vs Custom EVAL vs ADK EVAL

These are **not the same thing**.

### Pytest

`pytest` runs Python tests such as:

```text
test_jira_adapter.py
test_pdf_adapter.py
```

It checks whether the Python implementation behaves correctly.

For example:

```text
JiraAdapter
    ↓
Can it fetch KAN-4?
    ↓
Does it create Requirement?
    ↓
PASS / FAIL
```

### Custom EVAL

Custom EVAL evaluates the generated feature against project-specific QA/requirement rules.

For example:

```text
Requirement
    ↓
Generated Feature
    ↓
Does feature cover requirement?
    ↓
PASS / FAIL
```

### ADK EVAL

ADK EVAL evaluates the behavior/output of the Google ADK agent against an evaluation set.

So the three layers have different responsibilities:

```text
pytest
  │
  └── Tests Python implementation
            │
            ▼
Custom EVAL
  │
  └── Tests project-specific requirement coverage
            │
            ▼
ADK EVAL
  │
  └── Tests agent behavior/output
            │
            ▼
Final QA Gate
```

---

# 🧪 Step 22 — Run Python Tests

Run all adapter tests:

```powershell
python -m pytest evals/requirements/tests -v -s
```

For Jira only:

```powershell
python -m pytest evals/requirements/tests/test_jira_adapter.py -v -s
```

For the real Jira integration test:

```powershell
python -m pytest evals/requirements/tests/test_jira_adapter.py::test_fetch_real_jira_ticket -v -s
```

---

# 🔄 End-to-End Flow

The complete current architecture is:

```text
                    Jira / PDF
                       │
                       ▼
                Requirement Adapter
                       │
                       ▼
                  Requirement
                       │
                       ▼
                Google ADK Agent
                       │
                       ▼
             Requirement Analysis
                       │
                       ▼
              Gherkin Generation
                       │
                       ▼
              save_feature_file()
                       │
                       ▼
                .feature File
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        Custom EVAL           ADK EVAL
             │                   │
             └─────────┬─────────┘
                       ▼
                  Final QA Gate
                       │
                 ┌─────┴─────┐
                 ▼           ▼
                PASS         FAIL
                 │
                 ▼
             Git / GitHub
```

---

# 🌿 GitHub Workflow

Check the current changes:

```powershell
git status
```

Stage the changes:

```powershell
git add .
```

Verify:

```powershell
git status
```

Commit:

```powershell
git commit -m "Add Jira requirement adapter and QA evaluation flow"
```

Push:

```powershell
git push origin main
```

Verify:

```powershell
git status
```

Expected:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

---

# 🔐 Security

Never commit:

```text
.env
```

or API tokens/passwords.

The `.env` file should remain local.

Example:

```env
GOOGLE_API_KEY=...
JIRA_BASE_URL=...
JIRA_EMAIL=...
JIRA_API_TOKEN=...
```

Make sure `.gitignore` contains:

```text
.env
```

---

# 🚀 Future Roadmap

Possible future improvements:

- Jira requirement ingestion
- PDF requirement ingestion
- Confluence requirement ingestion
- Word document requirement ingestion
- Image and diagram understanding
- Attachment-aware requirement analysis
- Retrieval-Augmented Generation (RAG)
- Requirement chunking and embeddings
- Vector database integration
- Automated feature-file generation
- Automated test-case generation
- Playwright automation generation
- Requirement-to-test traceability
- Automated evaluation
- Automated QA gates
- CI/CD integration
- GitHub Actions
- Defect creation from failed tests

### Future Architecture

```text
Jira
PDF
Confluence
Word
Images
Diagrams
   │
   ▼
Requirement Adapters
   │
   ▼
Requirement Model
   │
   ▼
RAG / Knowledge Retrieval
   │
   ▼
Google ADK Agent
   │
   ▼
BDD Feature
   │
   ▼
Test Cases
   │
   ▼
Playwright Automation
   │
   ▼
Test Execution
   │
   ▼
Evaluation
   │
   ▼
QA Gate
   │
   ▼
CI/CD
```

---

# 🎯 Project Vision

The long-term goal is to build an AI-powered QA Engineering workflow where a requirement can flow through the testing lifecycle with minimal manual effort:

```text
Requirement
     ↓
Requirement Understanding
     ↓
BDD Feature
     ↓
Test Cases
     ↓
Automation Code
     ↓
Execution
     ↓
Evaluation
     ↓
QA Gate
     ↓
CI/CD
```

The project is being developed incrementally so that each stage can be understood, tested, evaluated, and integrated before moving to the next stage.
