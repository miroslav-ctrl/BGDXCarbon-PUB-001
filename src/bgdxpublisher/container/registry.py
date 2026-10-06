"""Typed service registry."""

from typing import TypeVar, cast

from bgdxpublisher.exceptions import RuntimeFoundationError

T = TypeVar("T")


class ServiceRegistryError(RuntimeFoundationError):
    """Base class for service registry errors."""


class DuplicateServiceError(ServiceRegistryError):
    """Raised when a service type is already registered."""


class ServiceNotFoundError(ServiceRegistryError):
    """Raised when a requested service type is not registered."""


class ServiceTypeMismatchError(ServiceRegistryError):
    """Raised when a service does not match its declared type."""


class ServiceRegistry:
    """Store and resolve services by their declared type."""

    def __init__(self) -> None:
        """Create an empty service registry."""
        self._services: dict[type[object], object] = {}

    def register(self, service_type: type[T], service: T) -> None:
        """Register a service instance under its type.

        Args:
            service_type: Type used as the service key.
            service: Instance to register.

        Raises:
            DuplicateServiceError: If this service type is registered already.
            ServiceTypeMismatchError: If the instance is not of the declared type.
        """
        if service_type in self._services:
            raise DuplicateServiceError(
                f"Service type '{service_type.__name__}' is already registered."
            )
        if not isinstance(service, service_type):
            raise ServiceTypeMismatchError(
                f"Service must be an instance of '{service_type.__name__}'."
            )
        self._services[service_type] = service

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a registered service by type.

        Args:
            service_type: Type used as the service key.

        Raises:
            ServiceNotFoundError: If this service type is not registered.
        """
        try:
            service = self._services[service_type]
        except KeyError as error:
            raise ServiceNotFoundError(
                f"Service type '{service_type.__name__}' is not registered."
            ) from error
        return cast(T, service)

    def contains(self, service_type: type[object]) -> bool:
        """Return whether a service type is registered."""
        return service_type in self._services

    def clear(self) -> None:
        """Remove all registered services."""
        self._services.clear()
