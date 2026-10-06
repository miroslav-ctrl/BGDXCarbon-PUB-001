"""Runtime-domain exceptions."""

from bgdxpublisher.exceptions import RuntimeFoundationError

__all__ = [
    "ApplicationInitializationError",
    "ApplicationShutdownError",
    "InvalidLifecycleTransitionError",
    "RuntimeFoundationError",
]


class InvalidLifecycleTransitionError(RuntimeFoundationError):
    """Raised when an application lifecycle transition is not permitted."""


class ApplicationInitializationError(RuntimeFoundationError):
    """Raised when application initialization fails."""


class ApplicationShutdownError(RuntimeFoundationError):
    """Raised when application shutdown fails."""
