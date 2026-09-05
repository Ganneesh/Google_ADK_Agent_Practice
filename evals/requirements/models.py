from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional


@dataclass
class RequirementEvidence:
    """One piece of raw evidence backing the requirement — an image,
    a PDF attachment, etc. Preserved for traceability and optional
    multimodal use later."""
    kind: Literal["text", "image", "pdf", "table"]
    content: bytes | str
    description: Optional[str] = None  # populated for image/pdf kinds
    filename: Optional[str] = None


@dataclass
class Requirement:
    """The canonical, source-agnostic representation every downstream
    consumer (agent, coverage evaluator) reads from. No consumer should
    ever see a raw Jira/Confluence/PDF object directly."""
    id: str                                    # "PROJ-1234", "confl-98213", file hash, etc.
    source_system: str                          # "jira" | "confluence" | "docx" | "pdf" | "text"
    title: str
    narrative: str                               # normalized prose description
    acceptance_criteria: list[str] = field(default_factory=list)
    evidence: list[RequirementEvidence] = field(default_factory=list)
    fetched_at: datetime = field(default_factory=datetime.now)
    source_version: Optional[str] = None

    def to_prompt_text(self) -> str:
        """Renders the requirement as a single text block, for consumers
        (like the agent or coverage evaluator) that only accept plain text."""
        parts = [self.narrative]
        if self.acceptance_criteria:
            parts.append("\nAcceptance Criteria:")
            parts.extend(f"- {ac}" for ac in self.acceptance_criteria)
        if self.evidence:
            described = [e.description for e in self.evidence if e.description]
            if described:
                parts.append("\nAttached Evidence (described):")
                parts.extend(f"- {d}" for d in described)
        return "\n".join(parts)