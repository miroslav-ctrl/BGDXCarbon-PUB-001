"""Tests for diagnostic orchestration."""

from bgdxpublisher.diagnostics import (
    DiagnosticCheck,
    DiagnosticResult,
    DiagnosticService,
    DiagnosticStatus,
)


def test_service_runs_all_checks_in_order() -> None:
    executed: list[str] = []

    def passing_check() -> DiagnosticResult:
        executed.append("pass")
        return DiagnosticResult("pass", DiagnosticStatus.PASS, "OK.")

    def warning_check() -> DiagnosticResult:
        executed.append("warning")
        return DiagnosticResult(
            "warning", DiagnosticStatus.WARNING, "Review.", mandatory=False
        )

    report = DiagnosticService(
        (
            DiagnosticCheck("pass", passing_check),
            DiagnosticCheck("warning", warning_check),
        )
    ).run()

    assert executed == ["pass", "warning"]
    assert [result.name for result in report.results] == ["pass", "warning"]
    assert report.exit_code == 0


def test_service_converts_unexpected_errors_to_failures() -> None:
    def broken_check() -> DiagnosticResult:
        raise RuntimeError("broken")

    report = DiagnosticService((DiagnosticCheck("broken", broken_check),)).run()

    assert report.exit_code == 1
    assert report.results[0].status is DiagnosticStatus.FAIL
    assert report.results[0].message == "Unexpected error: broken"
