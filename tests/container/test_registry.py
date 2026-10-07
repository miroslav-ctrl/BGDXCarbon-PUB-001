"""Tests for typed service registration and resolution."""

import pytest

from bgdxpublisher.container import (
    DuplicateServiceError,
    ServiceNotFoundError,
    ServiceRegistry,
    ServiceTypeMismatchError,
)


class ExampleService:
    """Simple test service."""


def test_registry_registers_resolves_and_clears_services() -> None:
    registry = ServiceRegistry()
    service = ExampleService()
    assert not registry.contains(ExampleService)
    registry.register(ExampleService, service)
    assert registry.contains(ExampleService)
    assert registry.resolve(ExampleService) is service
    registry.clear()
    assert not registry.contains(ExampleService)


def test_registry_rejects_duplicate_service_type() -> None:
    registry = ServiceRegistry()
    registry.register(ExampleService, ExampleService())
    with pytest.raises(DuplicateServiceError):
        registry.register(ExampleService, ExampleService())


def test_registry_rejects_wrong_instance_type() -> None:
    with pytest.raises(ServiceTypeMismatchError):
        ServiceRegistry().register(ExampleService, object())  # type: ignore[arg-type]


def test_registry_reports_missing_service() -> None:
    with pytest.raises(ServiceNotFoundError):
        ServiceRegistry().resolve(ExampleService)
