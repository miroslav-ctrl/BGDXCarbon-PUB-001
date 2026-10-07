"""Validated runtime configuration models."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ApplicationSettings(BaseModel):
    """Publisher application identity settings."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    version: str


class RuntimeSettings(BaseModel):
    """Runtime environment settings."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    environment: str = "development"


class LoggingSettings(BaseModel):
    """Standard-library logging settings."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    console: bool = True
    file: Path | None = None


class PublisherSettings(BaseModel):
    """Fully validated and immutable publisher configuration."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    app: ApplicationSettings
    runtime: RuntimeSettings = RuntimeSettings()
    logging: LoggingSettings = LoggingSettings()
