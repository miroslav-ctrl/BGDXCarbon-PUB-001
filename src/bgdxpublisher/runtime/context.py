"""Runtime context and application metadata."""

from dataclasses import dataclass

from bgdxpublisher.container import ServiceRegistry

from .lifecycle import ApplicationLifecycle, RuntimeState


@dataclass(frozen=True, slots=True)
class ApplicationMetadata:
    """Immutable application identity and environment metadata.

    Attributes:
        name: Application name from validated configuration.
        version: Application version from validated configuration.
        environment: Selected runtime environment.
    """

    name: str
    version: str
    environment: str = "development"


@dataclass(slots=True)
class RuntimeContext:
    """Mutable runtime coordination context."""

    metadata: ApplicationMetadata
    lifecycle: ApplicationLifecycle
    services: ServiceRegistry

    @property
    def state(self) -> RuntimeState:
        """Return the current lifecycle state."""
        return self.lifecycle.state
