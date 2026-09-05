from typing import Protocol
from evals.requirements.models import Requirement


class RequirementSourceAdapter(Protocol):
    """Every requirement source implements exactly this one method.
    Nothing downstream needs to know which systems exist."""

    def fetch(self, locator: str) -> Requirement:
        ...


class RequirementFetchError(Exception):
    """Raised when a source cannot be reached or parsed. Never swallow
    this into an empty Requirement — that would let coverage checks
    pass vacuously against nothing."""
    pass