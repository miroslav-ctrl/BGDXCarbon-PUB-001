"""Tests for command-line parsing and dispatch."""

from io import StringIO
from pathlib import Path

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.cli.doctor import format_report, run_doctor
from bgdxpublisher.cli.version import show_version
from bgdxpublisher.diagnostics import (
    DiagnosticResult,
    DiagnosticService,
    DiagnosticStatus,
)


def test_help_lists_all_required_commands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["--help"])

    assert error.value.code == 0
    help_text = capsys.readouterr().out
    assert "version" in help_text
    assert "doctor" in help_text
    assert "config" in help_text
    assert "runtime" in help_text


def test_no_arguments_displays_help() -> None:
    output = StringIO()

    assert main([], output) == 0
    assert "usage: bgdxpublisher" in output.getvalue()


@pytest.mark.parametrize("arguments", [["config"], ["runtime"]])
def test_nested_commands_require_subcommand(arguments: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(arguments, StringIO())

    assert error.value.code == 2


def test_version_reports_required_runtime_information() -> None:
    output = StringIO()

    assert main(["version"], output) == 0
    rendered = output.getvalue()
    assert "Application: BGDXCarbon Publisher Suite" in rendered
    assert "Application version: 0.1.0" in rendered
    assert "Python version:" in rendered
    assert "Runtime environment: development" in rendered


def test_version_uses_selected_environment_and_interpreter() -> None:
    output = StringIO()

    assert (
        show_version(
            output,
            environ={"BGDXPUBLISHER_ENV": "production"},
            python_version="3.13.1",
        )
        == 0
    )
    assert "Python version: 3.13.1" in output.getvalue()
    assert "Runtime environment: production" in output.getvalue()


def test_doctor_formats_all_pass_results_and_returns_zero() -> None:
    service = DiagnosticService(
        (
            lambda: DiagnosticResult("Python", DiagnosticStatus.PASS, "supported"),
            lambda: DiagnosticResult("Runtime", DiagnosticStatus.PASS, "ready"),
        )
    )
    output = StringIO()

    assert run_doctor(output, Path("unused.yaml"), service) == 0
    rendered = output.getvalue()
    assert "Python ................ PASS" in rendered
    assert "Overall .............. READY" in rendered


def test_doctor_warning_does_not_return_failure() -> None:
    service = DiagnosticService(
        (lambda: DiagnosticResult("Logging", DiagnosticStatus.WARNING, "optional"),)
    )
    output = StringIO()

    assert run_doctor(output, Path("unused.yaml"), service) == 0
    assert "WARNING" in output.getvalue()
    assert "READY WITH WARNINGS" in output.getvalue()


def test_doctor_mandatory_failure_returns_one() -> None:
    service = DiagnosticService(
        (lambda: DiagnosticResult("Runtime", DiagnosticStatus.FAIL, "unavailable"),)
    )
    output = StringIO()

    assert run_doctor(output, Path("unused.yaml"), service) == 1
    assert "NOT READY" in output.getvalue()


def test_format_empty_report_is_supported() -> None:
    assert "Overall" in format_report(DiagnosticService(()).run())
