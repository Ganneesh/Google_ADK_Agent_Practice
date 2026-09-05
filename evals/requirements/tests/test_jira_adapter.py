import pytest

from evals.requirements.jira_adapter import JiraAdapter
from evals.requirements.base import RequirementFetchError


def test_fetch_real_jira_ticket():
    """
    Integration test:
    Fetch the real Jira ticket KAN-4 and verify that
    JiraAdapter converts it into a Requirement object.
    """

    adapter = JiraAdapter()

    ticket = adapter._get_issue("KAN-4")

    print("\n========== RAW JIRA DESCRIPTION ==========")
    print(ticket["fields"]["description"])

    print("\n========== CONVERTED DESCRIPTION ==========")
    text = adapter._adf_to_text(ticket["fields"]["description"])
    print(text)

    print("\n========== EXTRACTED ACCEPTANCE CRITERIA ==========")
    criteria = adapter._extract_acceptance_criteria(ticket["fields"])
    print(criteria)

    requirement = adapter.fetch("KAN-4")

    print("\n========== REQUIREMENT ==========")
    print("ID:", requirement.id)
    print("Source:", requirement.source_system)
    print("Title:", requirement.title)
    print("Narrative:", requirement.narrative)
    print("Acceptance Criteria:", requirement.acceptance_criteria)
    print("Evidence Count:", len(requirement.evidence))
    print("Source Version:", requirement.source_version)

    assert requirement.id == "KAN-4"
    assert requirement.source_system == "jira"
    assert requirement.title
    assert requirement.narrative


def test_fetch_raises_on_missing_credentials(monkeypatch):
    """
    Verify that JiraAdapter fails when Jira credentials are missing.
    """

    monkeypatch.delenv("JIRA_BASE_URL", raising=False)
    monkeypatch.delenv("JIRA_EMAIL", raising=False)
    monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

    with pytest.raises(RequirementFetchError):
        JiraAdapter()


def test_fetch_raises_on_api_error(monkeypatch):
    """
    Verify that JiraAdapter raises RequirementFetchError
    when Jira returns an API error.
    """

    adapter = JiraAdapter()

    class FakeResponse:
        status_code = 404
        text = "Issue does not exist"

        def json(self):
            return {}

    monkeypatch.setattr(
        "evals.requirements.jira_adapter.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    with pytest.raises(RequirementFetchError):
        adapter.fetch("KAN-9999")