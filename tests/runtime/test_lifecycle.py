"""Tests for runtime lifecycle and metadata."""

from dataclasses import FrozenInstanceError

import pytest

from bgdxpublisher.container import ServiceRegistry
from bgdxpublisher.runtime import (
    ApplicationLifecycle,
    ApplicationMetadata,
    InvalidLifecycleTransitionError,
    RuntimeContext,
    RuntimeState,
)


def test_lifecycle_transitions_in_order() -> None:
    lifecycle = ApplicationLifecycle()
    for state in (
        RuntimeState.INITIALIZING,
        RuntimeState.CONFIGURED,
        RuntimeState.RUNNING,
        RuntimeState.STOPPING,
        RuntimeState.STOPPED,
    ):
        lifecycle.transition(state)
        assert lifecycle.state is state


def test_lifecycle_allows_failure_during_initialization() -> None:
    lifecycle = ApplicationLifecycle()
    lifecycle.transition(RuntimeState.INITIALIZING)
    lifecycle.transition(RuntimeState.FAILED)
    assert lifecycle.state is RuntimeState.FAILED


def test_lifecycle_allows_failure_from_running() -> None:
    lifecycle = ApplicationLifecycle()
    for state in (
        RuntimeState.INITIALIZING,
        RuntimeState.CONFIGURED,
        RuntimeState.RUNNING,
        RuntimeState.FAILED,
    ):
        lifecycle.transition(state)
    assert lifecycle.state is RuntimeState.FAILED


def test_lifecycle_rejects_invalid_transition() -> None:
    lifecycle = ApplicationLifecycle()
    with pytest.raises(InvalidLifecycleTransitionError):
        lifecycle.transition(RuntimeState.RUNNING)


def test_metadata_is_immutable_and_context_exposes_state() -> None:
    metadata = ApplicationMetadata(name="Publisher", version="1.0")
    context = RuntimeContext(metadata, ApplicationLifecycle(), ServiceRegistry())
    assert context.state is RuntimeState.CREATED
    with pytest.raises(FrozenInstanceError):
        metadata.name = "Changed"  # type: ignore[misc]
