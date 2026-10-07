"""Tests for CLI command behavior."""

from pathlib import Path

import pytest

from bgdxpublisher.cli.config import run_config_validate
from bgdxpublisher.cli.doctor import run_doctor
from bgdxpublisher.cli.runtime import run_runtime_status
from bgdxpublisher.diagnostics import (
    DiagnosticCheck,
    DiagnosticResult,
    DiagnosticStatus,
)


def _write_config(path: Path, *, console: bool = False) -> Path:
    path.write_text(
        "app:\n  name: Test Publisher\n  version: '1.2'\n"
        "runtime:\n  environment: test\n"
        f"logging:\n  console: {'true' if console else 'false'}\n",
        encoding="utf-8",
    )
    return path


def test_config_validate_success(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = _write_config(tmp_path / "config.yaml")
    assert run_config_validate(config) == 0
    assert "Configuration is valid." in capsys.readouterr().out


def test_config_validate_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run_config_validate(tmp_path / "missing.yaml") == 1
    assert "Configuration is invalid:" in capsys.readouterr().err


def test_runtime_status_uses_application_metadata_and_state(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    config = _write_config(tmp_path / "config.yaml")
    assert run_runtime_status(config) == 0
    output = capsys.readouterr().out
    assert "Application: Test Publisher" in output
    assert "Version: 1.2" in output
    assert "Environment: test" in output
    assert "State: CONFIGURED" in output


def test_runtime_status_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run_runtime_status(tmp_path / "missing.yaml") == 1
    assert "Unable to read runtime status:" in capsys.readouterr().err


def test_doctor_all_pass_and_exit_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("bgdxpublisher.diagnostics.checks.sys.version_info", (3, 13, 0))
    config = _write_config(tmp_path / "config.yaml")
    assert run_doctor(config) == 0
    output = capsys.readouterr().out
    assert output.count("PASS:") == 6
    assert "FAIL:" not in output


def test_doctor_mandatory_failure_returns_one(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("bgdxpublisher.diagnostics.checks.sys.version_info", (3, 13, 0))
    assert run_doctor(tmp_path / "missing.yaml") == 1
    assert "FAIL: configuration:" in capsys.readouterr().out


def test_doctor_warning_only_returns_zero(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    warning = DiagnosticResult(
        "workspace",
        DiagnosticStatus.WARNING,
        "Workspace cannot be read.",
        mandatory=False,
    )
    monkeypatch.setattr(
        "bgdxpublisher.cli.doctor.default_diagnostic_checks",
        lambda config_path: (DiagnosticCheck("workspace", lambda: warning),),
    )

    assert run_doctor(Path("unused.yaml")) == 0
    assert "WARNING: workspace: Workspace cannot be read." in capsys.readouterr().out
