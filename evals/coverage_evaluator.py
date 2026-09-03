import os
import json
import sys

from pathlib import Path
from dotenv import load_dotenv
from google import genai


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / "qa_agent" / ".env"

load_dotenv(ENV_FILE)


client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


def evaluate_coverage(requirement: str, feature: str) -> dict:

    prompt = f"""
You are a QA automation expert.

Compare the SOFTWARE REQUIREMENT with the GENERATED GHERKIN FEATURE.

Your job is to determine whether the generated Gherkin covers
the requirement correctly.

SOFTWARE REQUIREMENT:
{requirement}

GENERATED GHERKIN:
{feature}

Analyze the requirement semantically.

Return ONLY valid JSON in this format:

{{
  "coverage_score": 0,
  "status": "PASS",
  "covered_requirements": [],
  "missing_requirements": [],
  "extra_behavior": []
}}

Rules:

1. Break the requirement into meaningful testable expectations.
2. Check whether each expectation is covered by the Gherkin.
3. Do not require exact wording.
4. Understand equivalent meanings.
5. Identify missing requirements.
6. Identify behavior in Gherkin that is not supported by the requirement.
7. coverage_score must be between 0 and 100.
8. PASS only when all important requirements are covered.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    response_text = response.text.strip()

    # Remove markdown code fences if the model adds them
    if response_text.startswith("```json"):
        response_text = response_text[7:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    return json.loads(response_text.strip())


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print(
            "Usage: python coverage_evaluator.py "
            "<requirement_file> <feature_file>"
        )
        sys.exit(1)

    requirement_file = sys.argv[1]
    feature_file = sys.argv[2]

    with open(requirement_file, "r", encoding="utf-8") as file:
        requirement = file.read()

    with open(feature_file, "r", encoding="utf-8") as file:
        feature = file.read()

    result = evaluate_coverage(
        requirement,
        feature
    )

    print("\nRequirement Coverage")
    print("--------------------")
    print(
        f"Score  : {result['coverage_score']}%"
    )
    print(
        f"Status : {result['status']}"
    )

    print(
        f"Covered: {result['covered_requirements']}"
    )

    print(
        f"Missing: {result['missing_requirements']}"
    )

    print(
        f"Extra  : {result['extra_behavior']}"
    )