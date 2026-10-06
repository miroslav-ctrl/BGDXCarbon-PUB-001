"""Publisher application lifecycle orchestration."""

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

from bgdxpublisher.config import ConfigurationService, PublisherSettings
from bgdxpublisher.container import ServiceRegistry
from bgdxpublisher.logging import LoggerFactory, LoggingService
from bgdxpublisher.version import __version__

from .context import ApplicationMetadata, RuntimeContext
from .exceptions import (
    ApplicationInitializationError,
    ApplicationShutdownError,
    RuntimeFoundationError,
)
from .lifecycle import ApplicationLifecycle, RuntimeState


class PublisherApplication:
    """Initialize, start, and stop the publisher runtime."""

    def __init__(
        self,
        config_path: Path = Path("configs/default.yaml"),
        environment: str | None = None,
        environ: Mapping[str, str] | None = None,
        configuration: ConfigurationService | None = None,
        services: ServiceRegistry | None = None,
    ) -> None:
        """Create an application without starting its runtime.

        Args:
            config_path: YAML configuration file to load.
            environment: Optional environment configuration override.
            environ: Optional environment-variable mapping.
            configuration: Optional configuration service.
            services: Optional service registry.
        """
        self._environment = environment
        self._environ = environ
        self.configuration = configuration or ConfigurationService(config_path)
        self.context = RuntimeContext(
            metadata=ApplicationMetadata(
                name="BGDXCarbon Publisher Suite", version=__version__
            ),
            lifecycle=ApplicationLifecycle(),
            services=services or ServiceRegistry(),
        )
        self._logging: LoggingService | None = None

    @property
    def state(self) -> RuntimeState:
        """Return the current application state."""
        return self.context.state

    def initialize(self) -> None:
        """Load configuration and initialize runtime services.

        Raises:
            ApplicationInitializationError: If initialization fails.
        """
        self.context.lifecycle.transition(RuntimeState.INITIALIZING)
        try:
            settings = self.configuration.load(
                environment=self._environment, environ=self._environ
            )
            self.context.metadata = replace(
                self.context.metadata, environment=settings.runtime.environment
            )
            self.context.services.register(PublisherSettings, settings)
            self._logging = LoggerFactory.create("bgdxpublisher", settings.logging)
            self.context.services.register(LoggingService, self._logging)
            self.context.lifecycle.transition(RuntimeState.INITIALIZED)
        except Exception as error:
            self.context.lifecycle.transition(RuntimeState.FAILED)
            if self._logging is not None:
                self._logging.close()
            if isinstance(error, RuntimeFoundationError):
                raise
            raise ApplicationInitializationError(
                "Application initialization failed."
            ) from error

    def start(self) -> None:
        """Start the initialized application."""
        self.context.lifecycle.transition(RuntimeState.RUNNING)

    def stop(self) -> None:
        """Stop the application and release runtime logging resources.

        Raises:
            ApplicationShutdownError: If shutdown fails.
        """
        self.context.lifecycle.transition(RuntimeState.STOPPING)
        try:
            if self._logging is not None:
                self._logging.close()
            self.context.lifecycle.transition(RuntimeState.STOPPED)
        except Exception as error:
            self.context.lifecycle.transition(RuntimeState.FAILED)
            if isinstance(error, RuntimeFoundationError):
                raise
            raise ApplicationShutdownError("Application shutdown failed.") from error
