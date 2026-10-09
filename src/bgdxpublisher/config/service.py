"""YAML configuration loading and environment overrides."""

import json
import os
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .exceptions import (
    ConfigurationAlreadyLoadedError,
    ConfigurationFileError,
    ConfigurationNotLoadedError,
    ConfigurationValidationError,
)
from .models import PublisherSettings


class ConfigurationService:
    """Load and retain immutable validated application configuration."""

    def __init__(self, path: Path | None = None) -> None:
        """Create a configuration service for a YAML file.

        Args:
            path: Configuration file, or None to use the packaged default.
        """
        self._path = (
            files("bgdxpublisher.config").joinpath("default.yaml")
            if path is None
            else path
        )
        self._settings: PublisherSettings | None = None

    @property
    def settings(self) -> PublisherSettings:
        """Return validated settings after the first successful load.

        Raises:
            ConfigurationNotLoadedError: If configuration has not been loaded.
        """
        if self._settings is None:
            raise ConfigurationNotLoadedError("Configuration has not been loaded.")
        return self._settings

    def load(
        self,
        environment: str | None = None,
        environ: Mapping[str, str] | None = None,
    ) -> PublisherSettings:
        """Load, merge, validate, and freeze configuration.

        Args:
            environment: Optional environment-specific configuration name.
            environ: Optional environment-variable mapping.

        Raises:
            ConfigurationAlreadyLoadedError: If settings were already loaded.
            ConfigurationFileError: If the file cannot be read or parsed.
            ConfigurationValidationError: If the merged settings are invalid.
        """
        if self._settings is not None:
            raise ConfigurationAlreadyLoadedError(
                "Configuration is immutable after it has been loaded."
            )
        try:
            loaded = yaml.safe_load(self._path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as error:
            raise ConfigurationFileError(
                f"Unable to read configuration file: {self._path}"
            ) from error
        if not isinstance(loaded, Mapping):
            raise ConfigurationFileError("Configuration root must be a YAML mapping.")

        values = dict(loaded)
        variables = os.environ if environ is None else environ
        runtime_values = values.get("runtime", {})
        if not isinstance(runtime_values, Mapping):
            raise ConfigurationValidationError(
                "Configuration 'runtime' value must be a mapping."
            )
        configured_environment = environment
        if configured_environment is None:
            configured_environment = variables.get("BGDXPUBLISHER_ENV")
        if configured_environment is None:
            configured_environment = runtime_values.get("environment", "development")
        if not isinstance(configured_environment, str) or not configured_environment:
            raise ConfigurationValidationError(
                "The runtime environment must be a non-empty string."
            )
        environment_overrides = values.pop("environments", {})
        if not isinstance(environment_overrides, dict):
            raise ConfigurationFileError(
                "Configuration 'environments' value must be a mapping."
            )
        override = environment_overrides.get(configured_environment, {})
        if not isinstance(override, dict):
            raise ConfigurationFileError(
                f"Overrides for '{configured_environment}' must be a mapping."
            )
        _merge(values, override)
        values.setdefault("runtime", {})["environment"] = configured_environment
        _apply_environment_variables(values, variables)
        try:
            self._settings = PublisherSettings.model_validate(values)
        except ValidationError as error:
            raise ConfigurationValidationError(
                "Configuration values failed validation."
            ) from error
        return self._settings


def _merge(target: dict[str, Any], override: Mapping[str, Any]) -> None:
    """Recursively merge mapping values without mutating source mappings."""
    for key, value in override.items():
        current = target.get(key)
        if isinstance(current, dict) and isinstance(value, Mapping):
            _merge(current, value)
        else:
            target[key] = value


def _apply_environment_variables(
    values: dict[str, Any], environ: Mapping[str, str]
) -> None:
    """Apply nested ``BGDXPUBLISHER__`` overrides to configuration."""
    prefix = "BGDXPUBLISHER__"
    for key, value in environ.items():
        if not key.startswith(prefix):
            continue
        path = key[len(prefix) :].lower().split("__")
        if not all(path):
            continue
        current = values
        for part in path[:-1]:
            nested = current.get(part)
            if not isinstance(nested, dict):
                nested = {}
                current[part] = nested
            current = nested
        try:
            current[path[-1]] = json.loads(value)
        except json.JSONDecodeError:
            current[path[-1]] = value
