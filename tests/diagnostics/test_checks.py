"""Tests for individual diagnostic checks."""

import logging
import sys
from pathlib import Path

import pytest

from bgdxpublisher.diagnostics.checks import (
    check_configuration,
    check_logging_initialization,
    check_python_version,
    check_runtime_initialization,
    check_service_registry,
    check_workspace_accessibility,
)
from bgdxpublisher.diagnostics.models import DiagnosticStatus
from bgdxpublisher.logging import LoggingService
from bgdxpublisher.runtime import PublisherApplication, RuntimeState


def _write_config(path: Path) -> Path:
    path.write_text(
        "app:\n  name: Test Publisher\n  version: '1.2'\n"
        "runtime:\n  environment: test\nlogging:\n  console: false\n",
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    ("version", "expected"),
    [((3, 13, 0), DiagnosticStatus.PASS), ((3, 12, 9), DiagnosticStatus.FAIL)],
)
def test_python_version_check(
    monkeypatch: pytest.MonkeyPatch,
    version: tuple[int, int, int],
    expected: DiagnosticStatus,
) -> None:
    monkeypatch.setattr(sys, "version_info", version)

    assert check_python_version().status is expected


def test_configuration_check_success_and_failure(tmp_path: Path) -> None:
    config = _write_config(tmp_path / "config.yaml")

    assert check_configuration(config).status is DiagnosticStatus.PASS
    assert (
        check_configuration(tmp_path / "missing.yaml").status is DiagnosticStatus.FAIL
    )


@pytest.mark.parametrize(
    "check",
    [
        check_logging_initialization,
        check_service_registry,
        check_runtime_initialization,
    ],
)
def test_application_diagnostic_checks_pass(tmp_path: Path, check: object) -> None:
    config = _write_config(tmp_path / "config.yaml")

    result = check(config)  # type: ignore[operator]

    assert result.status is DiagnosticStatus.PASS


def test_workspace_check_reports_pass_and_nonmandatory_warning(
    tmp_path: Path,
) -> None:
    accessible = check_workspace_accessibility(tmp_path)
    inaccessible = check_workspace_accessibility(tmp_path / "missing")

    assert accessible.status is DiagnosticStatus.PASS
    assert inaccessible.status is DiagnosticStatus.WARNING
    assert inaccessible.mandatory is False


def test_logging_check_failure_closes_initialized_application(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _write_config(tmp_path / "config.yaml")
    wrong_logger = LoggingService(logging.getLogger("unexpected"), [])
    monkeypatch.setattr(
        "bgdxpublisher.runtime.application.LoggerFactory.create",
        staticmethod(lambda _name, _settings: wrong_logger),
    )

    result = check_logging_initialization(config)

    assert result.status is DiagnosticStatus.FAIL
    assert result.message == "Application logger has an unexpected name."


def test_runtime_check_rejects_unexpected_metadata_type(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _write_config(tmp_path / "config.yaml")
    monkeypatch.setattr("bgdxpublisher.diagnostics.checks.ApplicationMetadata", tuple)

    result = check_runtime_initialization(config)

    assert result.status is DiagnosticStatus.FAIL
    assert result.message == "Application metadata is unavailable."


def test_runtime_check_rejects_unexpected_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _write_config(tmp_path / "config.yaml")
    monkeypatch.setattr(
        "bgdxpublisher.diagnostics.checks.RuntimeState",
        type("UnexpectedState", (), {"CONFIGURED": RuntimeState.RUNNING}),
    )

    result = check_runtime_initialization(config)

    assert result.status is DiagnosticStatus.FAIL
    assert "Unexpected initialized state" in result.message


def test_application_check_swallows_cleanup_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FailingStopApplication(PublisherApplication):
        def stop(self) -> None:
            raise RuntimeError("shutdown failed")

    config = _write_config(tmp_path / "config.yaml")
    monkeypatch.setattr(
        "bgdxpublisher.diagnostics.checks.PublisherApplication",
        FailingStopApplication,
    )

    result = check_runtime_initialization(config)

    assert result.status is DiagnosticStatus.FAIL
    assert result.message == "shutdown failed"
