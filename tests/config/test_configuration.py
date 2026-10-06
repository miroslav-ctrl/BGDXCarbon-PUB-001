"""Tests for validated configuration loading."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from bgdxpublisher.config import (
    ConfigurationAlreadyLoadedError,
    ConfigurationFileError,
    ConfigurationNotLoadedError,
    ConfigurationService,
    ConfigurationValidationError,
)


def _write_config(path: Path, content: str | None = None) -> Path:
    path.write_text(
        content
        or "app:\n  name: Publisher\n  version: '1.0'\n"
        "runtime:\n  environment: development\n"
        "logging:\n  level: INFO\n  console: true\n"
        "environments:\n  staging:\n    app:\n      name: Staging Publisher\n"
        "    logging:\n      level: DEBUG\n",
        encoding="utf-8",
    )
    return path


def test_configuration_merges_environment_and_variable_overrides(
    tmp_path: Path,
) -> None:
    service = ConfigurationService(_write_config(tmp_path / "config.yaml"))
    settings = service.load(
        environment="staging",
        environ={
            "BGDXPUBLISHER__APP__VERSION": '"2.0"',
            "BGDXPUBLISHER__LOGGING__CONSOLE": "false",
        },
    )
    assert settings.app.name == "Staging Publisher"
    assert settings.app.version == "2.0"
    assert settings.runtime.environment == "staging"
    assert settings.logging.level == "DEBUG"
    assert settings.logging.console is False
    assert service.settings is settings
    with pytest.raises(ValidationError):
        settings.app.name = "Mutable"


def test_environment_can_be_selected_from_environment_mapping(tmp_path: Path) -> None:
    settings = ConfigurationService(_write_config(tmp_path / "config.yaml")).load(
        environ={"BGDXPUBLISHER_ENV": "staging"}
    )
    assert settings.runtime.environment == "staging"


def test_environment_string_override_and_invalid_nested_path(
    tmp_path: Path,
) -> None:
    service = ConfigurationService(_write_config(tmp_path / "config.yaml"))
    with pytest.raises(ConfigurationValidationError):
        service.load(environ={"BGDXPUBLISHER__APP__NAME__NESTED": "not-json"})


def test_configuration_must_be_loaded_before_access(tmp_path: Path) -> None:
    service = ConfigurationService(tmp_path / "config.yaml")
    with pytest.raises(ConfigurationNotLoadedError):
        _ = service.settings


def test_configuration_cannot_be_loaded_twice(tmp_path: Path) -> None:
    service = ConfigurationService(_write_config(tmp_path / "config.yaml"))
    service.load()
    with pytest.raises(ConfigurationAlreadyLoadedError):
        service.load()


@pytest.mark.parametrize(
    ("content", "error"),
    [
        ("[not, a, mapping]", ConfigurationFileError),
        ("app: [", ConfigurationFileError),
        ("app: {}\nenvironments: []", ConfigurationFileError),
        (
            "app:\n  name: Publisher\n  version: '1'\nruntime: []",
            ConfigurationValidationError,
        ),
        (
            "app:\n  name: Publisher\n  version: '1'\n" "environments:\n  staging: []",
            ConfigurationFileError,
        ),
        (
            "app:\n  name: Publisher\n  version: '1'\nlogging:\n  level: TRACE",
            ConfigurationValidationError,
        ),
    ],
)
def test_invalid_configuration_is_reported(
    tmp_path: Path, content: str, error: type[Exception]
) -> None:
    path = _write_config(tmp_path / "config.yaml", content)
    with pytest.raises(error):
        ConfigurationService(path).load(environment="staging")


def test_missing_configuration_file_is_reported(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationFileError):
        ConfigurationService(tmp_path / "missing.yaml").load()


def test_invalid_environment_name_is_reported(tmp_path: Path) -> None:
    path = _write_config(
        tmp_path / "config.yaml",
        "app:\n  name: Publisher\n  version: '1'\nruntime:\n  environment: []\n",
    )
    with pytest.raises(ConfigurationValidationError):
        ConfigurationService(path).load()


def test_empty_environment_argument_is_rejected(tmp_path: Path) -> None:
    service = ConfigurationService(_write_config(tmp_path / "config.yaml"))
    with pytest.raises(ConfigurationValidationError):
        service.load(environment="")


def test_empty_environment_variable_path_is_ignored(tmp_path: Path) -> None:
    service = ConfigurationService(_write_config(tmp_path / "config.yaml"))
    settings = service.load(environ={"BGDXPUBLISHER____APP": "invalid"})
    assert settings.app.name == "Publisher"
