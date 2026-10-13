"""Typed publisher pipeline exceptions."""

from bgdxpublisher.domain import PublisherDomainError

from .models import PipelineFailure, PipelineResult, PipelineStatus


class PipelineDefinitionError(PublisherDomainError):
    """Raised when a configured pipeline has invalid stage contracts."""


class PipelineInputContractError(PublisherDomainError):
    """Raised when a stage receives an input of the wrong type."""


class PipelineOutputContractError(PublisherDomainError):
    """Raised when a stage returns an output of the wrong type."""


class PipelineExecutionError(PublisherDomainError):
    """Raised after pipeline failure with a structured, non-success result."""

    def __init__(self, result: PipelineResult) -> None:
        """Retain the failed pipeline result and its structured failure."""
        if result.status is not PipelineStatus.FAILED or result.failure is None:
            raise ValueError("PipelineExecutionError requires a failed result.")
        self.result = result
        self.failure: PipelineFailure = result.failure
        super().__init__(
            f"Pipeline failed at {self.failure.stage_name}: {self.failure.error_code}."
        )
