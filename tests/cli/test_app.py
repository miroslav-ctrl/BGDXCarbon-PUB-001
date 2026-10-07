"""Tests for CLI parsing and top-level commands."""

from pathlib import Path

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.runtime import RuntimeFoundationError


def test_help_lists_supported_commands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["--help"])

    assert error.value.code == 0
    output = capsys.readouterr().out
    assert "version" in output
    assert "doctor" in output
    assert "config" in output
    assert "runtime" in output


def test_version_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["version"]) == 0
    assert "0.1.0" in capsys.readouterr().out


def test_no_arguments_preserves_application_startup(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main([]) == 0
    assert "started." in capsys.readouterr().err


def test_nested_command_help_is_available(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as error:
        main(["config", "validate", "--help"])

    assert error.value.code == 0
    assert "--config" in capsys.readouterr().out


def test_cli_accepts_path_arguments(tmp_path: Path) -> None:
    config = tmp_path / "missing.yaml"
    assert main(["config", "validate", "--config", str(config)]) == 1


def test_unselected_subcommand_displays_help(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["config"]) == 0
    assert "usage: bgdxpublisher" in capsys.readouterr().out


def test_default_startup_failure_returns_one(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    class BrokenApplication:
        def initialize(self) -> None:
            raise RuntimeFoundationError("initialization failed")

    monkeypatch.setattr("bgdxpublisher.cli.app.PublisherApplication", BrokenApplication)

    assert main([]) == 1
    assert "Unable to start application:" in capsys.readouterr().err
