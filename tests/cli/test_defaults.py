"""Regression tests for packaged defaults and explicit configuration paths."""

import json
from pathlib import Path

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.config import ConfigurationService


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        (["doctor"], "Overall .............. READY"),
        (["config", "validate"], "Configuration is valid."),
        (["runtime", "status"], "State: CONFIGURED"),
        (["version"], "Environment: development"),
        ([], "BGDXCarbon Publisher Suite 0.1.0 started."),
    ],
)
def test_default_commands_from_unrelated_directory(
    arguments: list[str],
    expected: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    # A conflicting CWD default must never replace the packaged resource.
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "default.yaml").write_text("invalid", encoding="utf-8")
    assert main(arguments) == 0
    captured = capsys.readouterr()
    assert expected in captured.out + captured.err


@pytest.mark.parametrize(
    "arguments", [["doctor"], ["config", "validate"], ["runtime", "status"]]
)
def test_explicit_config_overrides_packaged_default(
    arguments: list[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    config = tmp_path / "custom.yaml"
    config.write_text(
        "app:\n  name: Custom Publisher\n  version: '9.8.7'\n"
        "runtime:\n  environment: staging\n",
        encoding="utf-8",
    )
    assert main([*arguments, "--config", str(config)]) == 0
    output = capsys.readouterr().out
    if arguments == ["runtime", "status"]:
        assert "Application: Custom Publisher" in output
        assert "Version: 9.8.7" in output
        assert "Environment: staging" in output
    config.write_text("invalid", encoding="utf-8")
    assert main([*arguments, "--config", str(config)]) == 1


def test_packaged_configuration_works_without_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    settings = ConfigurationService().load(environ={})
    assert settings.app.name == "BGDXCarbon Publisher Suite"
    assert settings.app.version == "0.1.0"
    assert settings.runtime.environment == "development"


def test_version_uses_configuration_overrides(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("BGDXPUBLISHER__APP__NAME", "Custom Publisher")
    monkeypatch.setenv("BGDXPUBLISHER__APP__VERSION", "9.8.7")
    monkeypatch.setenv("BGDXPUBLISHER_ENV", "staging")
    assert main(["version"]) == 0
    output = capsys.readouterr().out
    assert "Application: Custom Publisher" in output
    assert "Version: 9.8.7" in output
    assert "Environment: staging" in output
    assert main([]) == 0
    assert json.loads(capsys.readouterr().err)["message"] == (
        "BGDXCarbon Publisher Suite 9.8.7 started."
    )


def test_version_configuration_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("BGDXPUBLISHER__LOGGING__LEVEL", "INVALID")
    assert main(["version"]) == 1
    assert "Unable to read version information:" in capsys.readouterr().err
