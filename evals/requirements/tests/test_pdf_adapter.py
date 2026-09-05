from pathlib import Path
from unittest.mock import patch, MagicMock

import fitz
import pytest
from dotenv import load_dotenv

# .env is located at:
# Google_ADK_Agent_Practice/qa_agent/.env
#
# This must be loaded BEFORE importing PdfAdapter because
# pdf_adapter.py creates the Gemini client at module import time.
load_dotenv(
    Path(__file__).resolve().parents[3] / "qa_agent" / ".env"
)

from evals.requirements.pdf_adapter import PdfAdapter
from evals.requirements.base import RequirementFetchError


@pytest.fixture
def text_pdf_path(tmp_path) -> Path:
    """Builds a real, minimal PDF with an actual text layer."""
    pdf_path = tmp_path / "requirement.pdf"

    doc = fitz.open()
    page = doc.new_page()

    page.insert_text(
        (50, 72),
        "A registered user should be able to log in using valid credentials.\n\n"
        "Acceptance Criteria:\n"
        "- User must enter a valid username and password.\n"
        "- User is redirected to the dashboard after successful login.",
    )

    doc.save(pdf_path)
    doc.close()

    return pdf_path


@pytest.fixture
def scanned_pdf_path(tmp_path) -> Path:
    """Builds a PDF with a page that has NO text layer (simulating a
    scanned document), so the adapter must fall back to rasterizing
    and describing it via the vision model."""
    pdf_path = tmp_path / "scanned.pdf"

    doc = fitz.open()
    doc.new_page()  # blank page, no text inserted

    doc.save(pdf_path)
    doc.close()

    return pdf_path


def test_fetch_extracts_text_layer_directly(text_pdf_path):
    adapter = PdfAdapter()
    requirement = adapter.fetch(str(text_pdf_path))

    assert requirement.source_system == "pdf"
    assert requirement.title == "requirement"

    assert "registered user should be able to log in" in requirement.narrative

    assert len(requirement.evidence) == 0  # no rasterization needed for text-layer pages

    assert len(requirement.acceptance_criteria) == 2

    assert any(
        "valid username and password" in c
        for c in requirement.acceptance_criteria
    )

    assert any(
        "redirected to the dashboard" in c
        for c in requirement.acceptance_criteria
    )


@patch("evals.requirements.pdf_adapter._gemini_client")
def test_fetch_falls_back_to_vision_model_for_scanned_page(
    mock_gemini,
    scanned_pdf_path,
):
    mock_gemini.models.generate_content.return_value = MagicMock(
        text=(
            "A login form with username field, password field, "
            "and submit button."
        )
    )

    adapter = PdfAdapter()
    requirement = adapter.fetch(str(scanned_pdf_path))

    assert len(requirement.evidence) == 1

    assert requirement.evidence[0].kind == "image"

    assert "login form" in requirement.evidence[0].description

    assert "login form" in requirement.narrative


def test_fetch_raises_on_missing_file():
    adapter = PdfAdapter()

    with pytest.raises(RequirementFetchError):
        adapter.fetch("nonexistent_file.pdf")


def test_content_hash_is_stable_for_same_file(text_pdf_path):
    adapter = PdfAdapter()

    hash1 = adapter._content_hash(text_pdf_path)
    hash2 = adapter._content_hash(text_pdf_path)

    assert hash1 == hash2
    assert len(hash1) == 16