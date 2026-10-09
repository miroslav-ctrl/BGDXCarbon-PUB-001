"""Diagnostic check orchestration."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .models import DiagnosticReport, DiagnosticResult, DiagnosticStatus

DiagnosticCallable = Callable[[], DiagnosticResult]


@dataclass(frozen=True, slots=True)
class DiagnosticCheck:
    """Named callable diagnostic check."""

    name: str
    run: DiagnosticCallable


class DiagnosticService:
    """Execute diagnostics and collect their results into a report."""

    def __init__(self, checks: Sequence[DiagnosticCheck]) -> None:
        """Create a service for the supplied checks.

        Args:
            checks: Checks to execute in report order.
        """
        self._checks = tuple(checks)

    def run(self) -> DiagnosticReport:
        """Run all checks and return their results.

        Unexpected check exceptions are converted into mandatory failures so
        that one broken check does not prevent the remaining diagnostics.
        Broad Exception handling is intentional at this diagnostic boundary
        only; it must not be propagated into command or configuration handling.
        """
        results: list[DiagnosticResult] = []
        for check in self._checks:
            try:
                result = check.run()
            except Exception as error:
                result = DiagnosticResult(
                    name=check.name,
                    status=DiagnosticStatus.FAIL,
                    message=f"Unexpected error: {error}",
                )
            results.append(result)
        return DiagnosticReport(results=tuple(results))
