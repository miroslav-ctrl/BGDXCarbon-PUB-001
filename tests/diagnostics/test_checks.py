"""Tests for individual diagnostic checks."""

from pathlib import Path

import pytest

from bgdxpublisher.container import ServiceRegistry
from bgdxpublisher.diagnostics.checks import (
    check_configuration,
    check_logging,
    check_python_version,
    check_runtime,
    check_service_registry,
    check_workspace,
)
from bgdxpublisher.diagnostics.models import DiagnosticStatus
from bgdxpublisher.logging import LoggerFactory

_VALID_CONFIG = """\
app:
  name: Test Publisher
  version: 1.2.3
runtime:
  environment: test
"""


def test_python_version_check_accepts_minimum_and_newer_versions() -> None:
    assert check_python_version((3, 13, 0)).status is DiagnosticStatus.PASS
    assert check_python_version((3, 14, 1)).status is DiagnosticStatus.PASS


def test_python_version_check_rejects_older_versions() -> None:
    result = check_python_version((3, 12, 99))

    assert result.status is DiagnosticStatus.FAIL
    assert "Python 3.13 or newer" in result.message


def test_configuration_check_uses_application_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(_VALID_CONFIG, encoding="utf-8")

    result = check_configuration(config_path)

    assert result.name == "Configuration"
    assert result.status is DiagnosticStatus.PASS


def test_configuration_check_returns_domain_error(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text("app: {}\n", encoding="utf-8")

    result = check_configuration(config_path)

    assert result.status is DiagnosticStatus.FAIL
    assert result.message == "Configuration values failed validation."


def test_logging_check_initializes_and_closes_service() -> None:
    result = check_logging()

    assert result.name == "Logging"
    assert result.status is DiagnosticStatus.PASS


def test_logging_check_returns_initialization_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise OSError("logging unavailable")

    monkeypatch.setattr(LoggerFactory, "create", staticmethod(fail))

    result = check_logging()

    assert result.status is DiagnosticStatus.FAIL
    assert result.message == "logging unavailable"


def test_service_registry_check_registers_and_resolves() -> None:
    result = check_service_registry()

    assert result.name == "Service Registry"
    assert result.status is DiagnosticStatus.PASS


def test_service_registry_check_detects_unresolved_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ServiceRegistry, "resolve", lambda *args: object())

    result = check_service_registry()

    assert result.status is DiagnosticStatus.FAIL
    assert result.message == "Registry could not resolve a service."


def test_runtime_check_initializes_application(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(_VALID_CONFIG, encoding="utf-8")

    result = check_runtime(config_path)

    assert result.name == "Runtime"
    assert result.status is DiagnosticStatus.PASS


def test_runtime_check_returns_initialization_failure(tmp_path: Path) -> None:
    result = check_runtime(tmp_path / "missing.yaml")

    assert result.name == "Runtime"
    assert result.status is DiagnosticStatus.FAIL


def test_workspace_check_accepts_accessible_directory(tmp_path: Path) -> None:
    result = check_workspace(tmp_path)

    assert result.name == "Workspace"
    assert result.status is DiagnosticStatus.PASS


def test_workspace_check_rejects_missing_directory(tmp_path: Path) -> None:
    result = check_workspace(tmp_path / "missing")

    assert result.name == "Workspace"
    assert result.status is DiagnosticStatus.FAIL
