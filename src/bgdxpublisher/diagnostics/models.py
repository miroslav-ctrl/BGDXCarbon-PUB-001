"""Immutable diagnostic result and report models."""

from dataclasses import dataclass
from enum import Enum


class DiagnosticStatus(str, Enum):
    """Possible outcomes for a diagnostic check."""

    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass(frozen=True, slots=True)
class DiagnosticResult:
    """Result of one named diagnostic check.

    Attributes:
        name: Stable diagnostic check name.
        status: Outcome of the check.
        message: Human-readable result detail.
        mandatory: Whether failure affects the doctor exit code.
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
    def status(self) -> DiagnosticStatus:
        """Return the aggregate status of the report."""
        if any(
            result.status is DiagnosticStatus.FAIL and result.mandatory
            for result in self.results
        ):
            return DiagnosticStatus.FAIL
        if any(
            result.status is DiagnosticStatus.WARNING
            or result.status is DiagnosticStatus.FAIL
            for result in self.results
        ):
            return DiagnosticStatus.WARNING
        return DiagnosticStatus.PASS

    @property
    def exit_code(self) -> int:
        """Return one only when a mandatory check failed."""
        return int(
            any(
                result.status is DiagnosticStatus.FAIL and result.mandatory
                for result in self.results
            )
        )
