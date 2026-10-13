"""Pipeline stage contracts, context, and result models."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Protocol

from bgdxpublisher.jobs import PublisherJob


class PipelineStatus(str, Enum):
    """Possible outcomes of a pipeline execution."""

    COMPLETED = "completed"
    FAILED = "failed"


class PipelineStage(Protocol):
    """Contract implemented by one sequential pipeline stage."""

    name: str
    input_type: type[object]
    output_type: type[object]

    def execute(self, value: object, context: PipelineContext) -> object:
        """Execute this stage using a value satisfying its input contract."""


@dataclass(frozen=True, slots=True)
class PipelineFailure:
    """Safe structured details for one stage or cleanup failure."""

    stage_name: str
    error_code: str
    exception_type: str
    cleanup_exception_types: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Immutable success or failure result for one complete pipeline run."""

    status: PipelineStatus
    output: object | None
    completed_stages: tuple[str, ...]
    failure: PipelineFailure | None = None

    def __post_init__(self) -> None:
        """Ensure failures are never represented as successful results."""
        if (self.status is PipelineStatus.COMPLETED) != (self.failure is None):
            raise ValueError("Pipeline result status and failure must agree.")
        if self.status is PipelineStatus.FAILED and self.output is not None:
            raise ValueError("Failed pipeline results cannot expose partial output.")


@dataclass(slots=True)
class PipelineContext:
    """Per-run state and cleanup registrations shared by pipeline stages."""

    job: PublisherJob | None = None
    attributes: Mapping[str, object] = field(default_factory=dict)
    _cleanups: list[Callable[[], None]] = field(default_factory=list, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        """Take a read-only snapshot of stage context attributes."""
        self.attributes = MappingProxyType(dict(self.attributes))

    def register_cleanup(self, callback: Callable[[], None]) -> None:
        """Register a callback to run once after execution, in reverse order."""
        if self._closed:
            raise RuntimeError("Pipeline context is already closed.")
        self._cleanups.append(callback)

    def close(self) -> tuple[Exception, ...]:
        """Run all registered cleanup callbacks and return every failure."""
        if self._closed:
            return ()
        self._closed = True
        errors: list[Exception] = []
        for callback in reversed(self._cleanups):
            try:
                callback()
            except Exception as error:
                errors.append(error)
        self._cleanups.clear()
        return tuple(errors)
