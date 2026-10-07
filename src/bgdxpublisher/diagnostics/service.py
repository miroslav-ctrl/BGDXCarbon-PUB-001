"""Diagnostic check orchestration."""

from collections.abc import Callable, Iterable

from .models import DiagnosticReport, DiagnosticResult, DiagnosticStatus

DiagnosticCheck = Callable[[], DiagnosticResult]


class DiagnosticService:
    """Run diagnostic checks and aggregate their structured results."""

    def __init__(self, checks: Iterable[DiagnosticCheck]) -> None:
        """Create a diagnostic service.

        Args:
            checks: Ordered diagnostic checks to execute.
        """
        self._checks = tuple(checks)

    def run(self) -> DiagnosticReport:
        """Execute all checks and return their aggregated results."""
        results: list[DiagnosticResult] = []
        for check in self._checks:
            try:
                results.append(check())
            except Exception as error:
                name = getattr(
                    check,
                    "check_name",
                    getattr(check, "__name__", type(check).__name__),
                )
                results.append(
                    DiagnosticResult(
                        name=name,
                        status=DiagnosticStatus.FAIL,
                        message=f"Check raised {type(error).__name__}: {error}",
                    )
                )
        return DiagnosticReport(tuple(results))
