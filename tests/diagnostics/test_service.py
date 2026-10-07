"""Tests for diagnostic orchestration."""

from bgdxpublisher.diagnostics import (
    DiagnosticResult,
    DiagnosticService,
    DiagnosticStatus,
)


def test_diagnostic_service_runs_checks_in_order() -> None:
    executed: list[str] = []

    def first() -> DiagnosticResult:
        executed.append("first")
        return DiagnosticResult("first", DiagnosticStatus.PASS, "ok")

    def second() -> DiagnosticResult:
        executed.append("second")
        return DiagnosticResult("second", DiagnosticStatus.PASS, "ok")

    report = DiagnosticService((first, second)).run()

    assert executed == ["first", "second"]
    assert [result.name for result in report.results] == ["first", "second"]
    assert report.overall_status is DiagnosticStatus.PASS


def test_diagnostic_service_converts_unexpected_check_error_to_failure() -> None:
    def broken() -> DiagnosticResult:
        raise RuntimeError("check unavailable")

    report = DiagnosticService((broken,)).run()

    assert report.results[0].name == "broken"
    assert report.results[0].status is DiagnosticStatus.FAIL
    assert report.results[0].message == "Check raised RuntimeError: check unavailable"
