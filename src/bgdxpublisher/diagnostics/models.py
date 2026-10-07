"""Typed diagnostic results and reports."""

from dataclasses import dataclass
from enum import Enum


class DiagnosticStatus(Enum):
    """Outcome of an individual diagnostic check or report."""

    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass(frozen=True, slots=True)
class DiagnosticResult:
    """Result returned by one diagnostic check.

    Attributes:
        name: Human-readable name of the check.
        status: Structured outcome of the check.
        message: Short explanation of the outcome.
        mandatory: Whether a failure should make the report not ready.
    """

    name: str
    status: DiagnosticStatus
    message: str
    mandatory: bool = True


@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    """Immutable collection of diagnostic results."""

    results: tuple[DiagnosticResult, ...]

    @property
    def overall_status(self) -> DiagnosticStatus:
        """Return the aggregate outcome, considering mandatory failures."""
        if any(
            result.mandatory and result.status is DiagnosticStatus.FAIL
            for result in self.results
        ):
            return DiagnosticStatus.FAIL
        if any(result.status is DiagnosticStatus.WARNING for result in self.results):
            return DiagnosticStatus.WARNING
        return DiagnosticStatus.PASS

    @property
    def ready(self) -> bool:
        """Return whether all mandatory diagnostic checks passed."""
        return self.overall_status is not DiagnosticStatus.FAIL

    @property
    def exit_code(self) -> int:
        """Return the doctor command process exit code."""
        return 0 if self.ready else 1
