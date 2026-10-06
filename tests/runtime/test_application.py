"""Tests for publisher application lifecycle."""

import logging
from pathlib import Path
from typing import cast

import pytest

from bgdxpublisher.config import (
    ConfigurationAlreadyLoadedError,
    ConfigurationFileError,
    ConfigurationService,
)
from bgdxpublisher.container import DuplicateServiceError, ServiceRegistry
from bgdxpublisher.logging import LoggingService
from bgdxpublisher.runtime import (
    ApplicationInitializationError,
    ApplicationShutdownError,
    InvalidLifecycleTransitionError,
    PublisherApplication,
    RuntimeState,
)


def _write_config(path: Path) -> Path:
    path.write_text(
        "app:\n  name: Test Publisher\n  version: '1.2'\n"
        "runtime:\n  environment: test\nlogging:\n  console: false\n",
        encoding="utf-8",
    )
    return path


def test_application_initializes_starts_and_stops(tmp_path: Path) -> None:
    application = PublisherApplication(
        config_path=_write_config(tmp_path / "config.yaml")
    )
    application.initialize()
    assert application.state is RuntimeState.INITIALIZED
    assert application.context.metadata.environment == "test"
    application.start()
    assert application.state is RuntimeState.RUNNING
    application.stop()
    assert application.state is RuntimeState.STOPPED


def test_application_rejects_start_before_initialization(tmp_path: Path) -> None:
    application = PublisherApplication(config_path=tmp_path / "missing.yaml")
    with pytest.raises(InvalidLifecycleTransitionError):
        application.start()


def test_initialization_failure_marks_application_failed(tmp_path: Path) -> None:
    application = PublisherApplication(config_path=tmp_path / "missing.yaml")
    with pytest.raises(ConfigurationFileError):
        application.initialize()
    assert application.state is RuntimeState.FAILED


def test_unexpected_initialization_failure_is_wrapped() -> None:
    class BrokenConfiguration:
        def load(self, **_kwargs: object) -> None:
            raise OSError("unexpected")

    application = PublisherApplication(
        configuration=cast(ConfigurationService, BrokenConfiguration())
    )
    with pytest.raises(ApplicationInitializationError):
        application.initialize()
    assert application.state is RuntimeState.FAILED


def test_domain_initialization_failure_is_preserved(tmp_path: Path) -> None:
    configuration = ConfigurationService(_write_config(tmp_path / "config.yaml"))
    configuration.load()
    application = PublisherApplication(configuration=configuration)
    with pytest.raises(ConfigurationAlreadyLoadedError):
        application.initialize()
    assert application.state is RuntimeState.FAILED


def test_duplicate_logging_service_fails_initialization_and_closes_handlers(
    tmp_path: Path,
) -> None:
    services = ServiceRegistry()
    services.register(
        LoggingService,
        LoggingService(logging.getLogger("test.existing"), []),
    )
    application = PublisherApplication(
        config_path=_write_config(tmp_path / "config.yaml"), services=services
    )
    with pytest.raises(DuplicateServiceError):
        application.initialize()
    assert application.state is RuntimeState.FAILED


def test_unexpected_shutdown_failure_is_wrapped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    application = PublisherApplication(
        config_path=_write_config(tmp_path / "config.yaml")
    )
    application.initialize()
    application.start()
    logging_service = application.context.services.resolve(LoggingService)

    def fail_close() -> None:
        raise OSError("unexpected")

    monkeypatch.setattr(logging_service, "close", fail_close)
    with pytest.raises(ApplicationShutdownError):
        application.stop()
    assert application.state is RuntimeState.FAILED


def test_domain_shutdown_failure_is_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    application = PublisherApplication(
        config_path=_write_config(tmp_path / "config.yaml")
    )
    application.initialize()
    application.start()
    logging_service = application.context.services.resolve(LoggingService)

    def fail_close() -> None:
        raise InvalidLifecycleTransitionError("domain shutdown error")

    monkeypatch.setattr(logging_service, "close", fail_close)
    with pytest.raises(InvalidLifecycleTransitionError):
        application.stop()
    assert application.state is RuntimeState.FAILED
