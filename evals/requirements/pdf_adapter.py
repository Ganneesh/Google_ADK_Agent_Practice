import hashlib
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from dotenv import load_dotenv
from google import genai
import os

from evals.requirements.base import RequirementFetchError
from evals.requirements.models import Requirement, RequirementEvidence

load_dotenv()

_gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


class PdfAdapter:
    """Extracts requirement text from a PDF. Pages with an extractable
    text layer are read directly; pages with no text (scanned/image-only)
    are rasterized and described using the vision-capable model, so
    nothing is silently dropped."""

    def fetch(self, locator: str) -> Requirement:
        """`locator` is a filesystem path to the PDF."""
        path = Path(locator)
        if not path.exists():
            raise RequirementFetchError(f"PDF not found: {locator}")

        try:
            doc = fitz.open(path)
        except Exception as e:
            raise RequirementFetchError(f"Could not open PDF '{locator}': {e}") from e

        page_texts: list[str] = []
        evidence: list[RequirementEvidence] = []

        for page_num, page in enumerate(doc):
            text = page.get_text().strip()
            if text:
                page_texts.append(text)
            else:
                image_bytes = self._rasterize_page(page)
                description = self._describe_with_vision_model(image_bytes, page_num)
                page_texts.append(description)
                evidence.append(RequirementEvidence(
                    kind="image",
                    content=image_bytes,
                    description=description,
                    filename=f"page_{page_num + 1}.png",
                ))

        doc.close()

        full_text = "\n\n".join(page_texts).strip()
        if not full_text:
            raise RequirementFetchError(
                f"No extractable text or describable content found in '{locator}'"
            )

        return Requirement(
            id=self._content_hash(path),
            source_system="pdf",
            title=path.stem,
            narrative=full_text,
            acceptance_criteria=self._extract_acceptance_criteria(full_text),
            evidence=evidence,
            source_version=str(path.stat().st_mtime),
        )

    def _content_hash(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:16]

    def _rasterize_page(self, page) -> bytes:
        pix = page.get_pixmap(dpi=150)
        return pix.tobytes("png")

    def _describe_with_vision_model(self, image_bytes: bytes, page_num: int) -> str:
        try:
            response = _gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": f"This is page {page_num + 1} of a PDF with no "
                                      f"extractable text layer (likely scanned). "
                                      f"Transcribe or describe the requirement content, "
                                      f"UI mockup, or acceptance criteria shown, being "
                                      f"specific and testable."},
                            {"inline_data": {"mime_type": "image/png", "data": _b64(image_bytes)}},
                        ],
                    }
                ],
            )
            return response.text.strip()
        except Exception as e:
            return f"[Could not describe page {page_num + 1}: {e}]"

    def _extract_acceptance_criteria(self, text: str) -> list[str]:
        lowered = text.lower()
        if "acceptance criteria" not in lowered:
            return []

        idx = lowered.index("acceptance criteria")
        ac_section = text[idx:]
        lines = [
            line.strip(" -*\t")
            for line in ac_section.splitlines()
            if line.strip() and "acceptance criteria" not in line.lower()
        ]
        return [line for line in lines if line]


def _b64(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode()