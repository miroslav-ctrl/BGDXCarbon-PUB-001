"""Tests for structured diagnostics models."""

from bgdxpublisher.diagnostics import (
    DiagnosticReport,
    DiagnosticResult,
    DiagnosticStatus,
)


def test_all_pass_report_is_ready() -> None:
    report = DiagnosticReport(
        (DiagnosticResult("Python", DiagnosticStatus.PASS, "supported"),)
    )

    assert report.overall_status is DiagnosticStatus.PASS
    assert report.ready
    assert report.exit_code == 0


def test_warning_report_is_ready_without_failure_exit_code() -> None:
    report = DiagnosticReport(
        (DiagnosticResult("Optional", DiagnosticStatus.WARNING, "degraded"),)
    )

    assert report.overall_status is DiagnosticStatus.WARNING
    assert report.ready
    assert report.exit_code == 0


def test_mandatory_failure_report_is_not_ready() -> None:
    report = DiagnosticReport(
        (DiagnosticResult("Runtime", DiagnosticStatus.FAIL, "unavailable"),)
    )

    assert report.overall_status is DiagnosticStatus.FAIL
    assert not report.ready
    assert report.exit_code == 1


def test_optional_failure_does_not_make_report_unready() -> None:
    report = DiagnosticReport(
        (DiagnosticResult("Optional", DiagnosticStatus.FAIL, "unavailable", False),)
    )

    assert report.overall_status is DiagnosticStatus.PASS
    assert report.ready
    assert report.exit_code == 0


def test_empty_report_is_ready() -> None:
    report = DiagnosticReport(())

    assert report.overall_status is DiagnosticStatus.PASS
    assert report.ready
