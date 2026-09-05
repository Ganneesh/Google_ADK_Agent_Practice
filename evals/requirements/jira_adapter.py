import base64
import os
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv
from google import genai

from evals.requirements.base import RequirementFetchError
from evals.requirements.models import Requirement, RequirementEvidence


# Load environment variables from qa_agent/.env
load_dotenv(
    Path(__file__).resolve().parents[2] / "qa_agent" / ".env"
)

_gemini_client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)


class JiraAdapter:
    """
    Fetches a Jira ticket, extracts description + acceptance criteria,
    and describes any image/PDF attachments using the vision-capable model
    so they contribute to the requirement's plain-text narrative.
    """

    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL", "").rstrip("/")
        self.email = os.getenv("JIRA_EMAIL", "")
        self.api_token = os.getenv("JIRA_API_TOKEN", "")

        if not all([
            self.base_url,
            self.email,
            self.api_token
        ]):
            raise RequirementFetchError(
                "Missing JIRA_BASE_URL, JIRA_EMAIL, or "
                "JIRA_API_TOKEN in .env"
            )

        self._auth = (
            self.email,
            self.api_token
        )

    def fetch(self, locator: str) -> Requirement:
        """
        Fetch a Jira issue and convert it into a Requirement object.

        locator example:
            KAN-4
            PROJ-1234
        """

        ticket = self._get_issue(locator)
        fields = ticket.get("fields", {})

        description_text = self._adf_to_text(
            fields.get("description")
        )

        acceptance_criteria = self._extract_acceptance_criteria(
            fields
        )

        evidence = self._extract_attachments(
            fields
        )

        return Requirement(
            id=ticket["key"],
            source_system="jira",
            title=fields.get("summary", ""),
            narrative=description_text,
            acceptance_criteria=acceptance_criteria,
            evidence=evidence,
            source_version=fields.get("updated"),
        )

    def _get_issue(self, issue_key: str) -> dict[str, Any]:
        """
        Fetch a Jira issue using Jira REST API.
        """

        url = (
            f"{self.base_url}"
            f"/rest/api/3/issue/{issue_key}"
        )

        response = requests.get(
            url,
            auth=self._auth,
            headers={
                "Accept": "application/json"
            }
        )

        if response.status_code != 200:
            raise RequirementFetchError(
                f"Failed to fetch Jira issue '{issue_key}': "
                f"{response.status_code} "
                f"{response.text[:300]}"
            )

        return response.json()

    def _adf_to_text(
        self,
        adf_doc: Optional[dict]
    ) -> str:
        """
        Convert Jira's Atlassian Document Format (ADF)
        into clean plain text.
        """

        if not adf_doc:
            return ""

        lines: list[str] = []

        def walk(node: dict):
            node_type = node.get("type")

            # Normal text node
            if node_type == "text":
                lines.append(
                    node.get("text", "")
                )

            # Jira hard line break
            elif node_type == "hardBreak":
                lines.append("\n")

            # Recursively process child nodes
            for child in node.get("content", []) or []:
                walk(child)

            # Add newline after block-level nodes
            if node_type in (
                "paragraph",
                "heading",
                "listItem"
            ):
                lines.append("\n")

        walk(adf_doc)

        return "".join(lines).strip()

    def _extract_acceptance_criteria(
        self,
        fields: dict
    ) -> list[str]:
        """
        Extract acceptance criteria from Jira.

        Supports:

        1. Dedicated Jira custom field.
        2. Gherkin-style Given/When/Then criteria
           directly inside the description.
        3. Explicit 'Acceptance Criteria' section
           inside the description.
        """

        # ---------------------------------------------------------
        # 1. Check dedicated Jira custom fields
        # ---------------------------------------------------------

        for key, value in fields.items():

            if (
                key.startswith("customfield_")
                and isinstance(value, dict)
            ):
                text = self._adf_to_text(value)

                if text and (
                    "given" in text.lower()
                    or "should" in text.lower()
                ):
                    return self._split_criteria(text)

        # ---------------------------------------------------------
        # 2. Get description
        # ---------------------------------------------------------

        description_text = self._adf_to_text(
            fields.get("description")
        )

        if not description_text:
            return []

        lowered = description_text.lower()

        # ---------------------------------------------------------
        # 3. Explicit "Acceptance Criteria" section
        # ---------------------------------------------------------

        if "acceptance criteria" in lowered:

            idx = lowered.index(
                "acceptance criteria"
            )

            ac_section = description_text[idx:]

            return self._split_criteria(
                ac_section
            )

        # ---------------------------------------------------------
        # 4. Gherkin-style criteria directly in description
        # ---------------------------------------------------------

        if (
            "given" in lowered
            and "when" in lowered
            and "then" in lowered
        ):
            return self._extract_gherkin_criteria(
                description_text
            )

        # Nothing found
        return []

    def _split_criteria(
        self,
        text: str
    ) -> list[str]:
        """
        Split an acceptance-criteria section into
        individual non-empty lines.
        """

        lines = [
            line.strip(" -*\t")
            for line in text.splitlines()
            if (
                line.strip()
                and "acceptance criteria"
                not in line.lower()
            )
        ]

        return [
            line
            for line in lines
            if line
        ]

    def _extract_gherkin_criteria(
        self,
        text: str
    ) -> list[str]:
        """
        Extract complete Given/When/Then blocks.

        Example input:

            Given the user is registered
            When the user enters valid credentials
            And clicks Login
            Then the dashboard is displayed

            Given the user is registered
            When the user enters invalid credentials
            Then an error message is displayed

        Result:

            [
                "Given ... When ... And ... Then ...",
                "Given ... When ... Then ..."
            ]
        """

        criteria: list[str] = []
        current: list[str] = []

        for line in text.splitlines():

            line = line.strip()

            # Empty line means the current criterion is complete
            if not line:

                if current:
                    criteria.append(
                        " ".join(current)
                    )

                    current = []

                continue

            # Gherkin step
            if line.startswith(
                (
                    "Given ",
                    "When ",
                    "And ",
                    "Then ",
                )
            ):
                current.append(line)

        # Add final criterion
        if current:
            criteria.append(
                " ".join(current)
            )

        return criteria

    def _extract_attachments(
        self,
        fields: dict
    ) -> list[RequirementEvidence]:
        """
        Download image/PDF attachments from Jira
        and describe them using Gemini vision.
        """

        evidence: list[RequirementEvidence] = []

        for attachment in (
            fields.get("attachment", []) or []
        ):

            mime_type = attachment.get(
                "mimeType",
                ""
            )

            filename = attachment.get(
                "filename",
                ""
            )

            content_url = attachment.get(
                "content"
            )

            # Only process images and PDFs
            if not (
                mime_type.startswith("image/")
                or mime_type == "application/pdf"
            ):
                continue

            if not content_url:
                continue

            response = requests.get(
                content_url,
                auth=self._auth
            )

            if response.status_code != 200:
                continue

            file_bytes = response.content

            kind = (
                "image"
                if mime_type.startswith("image/")
                else "pdf"
            )

            description = (
                self._describe_with_vision_model(
                    file_bytes,
                    mime_type,
                    filename
                )
            )

            evidence.append(
                RequirementEvidence(
                    kind=kind,
                    content=file_bytes,
                    description=description,
                    filename=filename,
                )
            )

        return evidence

    def _describe_with_vision_model(
        self,
        file_bytes: bytes,
        mime_type: str,
        filename: str
    ) -> str:
        """
        Describe an image/PDF attachment using Gemini.
        """

        try:

            response = (
                _gemini_client
                .models
                .generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": (
                                        "Describe the software "
                                        "requirement, UI layout, "
                                        "or behavior shown in "
                                        f"this file ('{filename}'). "
                                        "Be specific and testable. "
                                        "Mention exact UI elements, "
                                        "text, or flows visible, "
                                        "since this will be used "
                                        "to generate test cases."
                                    )
                                },
                                {
                                    "inline_data": {
                                        "mime_type": mime_type,
                                        "data": (
                                            base64
                                            .b64encode(file_bytes)
                                            .decode()
                                        ),
                                    }
                                },
                            ],
                        }
                    ],
                )
            )

            return response.text.strip()

        except Exception as e:

            return (
                f"[Could not describe attachment "
                f"'{filename}': {e}]"
            )