"""Tests for diagnostic result and report models."""

from dataclasses import FrozenInstanceError

import pytest

from bgdxpublisher.diagnostics import (
    DiagnosticReport,
    DiagnosticResult,
    DiagnosticStatus,
)


def test_diagnostic_result_is_immutable() -> None:
    result = DiagnosticResult("config", DiagnosticStatus.PASS, "Valid.")

    with pytest.raises(FrozenInstanceError):
        result.name = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("result_status", "mandatory", "expected_status", "expected_exit"),
    [
        (DiagnosticStatus.PASS, True, DiagnosticStatus.PASS, 0),
        (DiagnosticStatus.WARNING, False, DiagnosticStatus.WARNING, 0),
        (DiagnosticStatus.FAIL, False, DiagnosticStatus.WARNING, 0),
        (DiagnosticStatus.FAIL, True, DiagnosticStatus.FAIL, 1),
    ],
)
def test_report_aggregate_status_and_exit_code(
    result_status: DiagnosticStatus,
    mandatory: bool,
    expected_status: DiagnosticStatus,
    expected_exit: int,
) -> None:
    result = DiagnosticResult("check", result_status, "detail", mandatory)

    report = DiagnosticReport((result,))

    assert report.status is expected_status
    assert report.exit_code == expected_exit


def test_empty_report_passes() -> None:
    report = DiagnosticReport(())

    assert report.status is DiagnosticStatus.PASS
    assert report.exit_code == 0
