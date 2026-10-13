"""Typed publisher job domain exceptions."""

from bgdxpublisher.domain import PublisherDomainError, ValidationResult


class JobValidationError(PublisherDomainError):
    """Raised when a job request contains validation errors."""

    def __init__(self, result: ValidationResult) -> None:
        """Create an error retaining stable structured validation issues."""
        self.result = result
        codes = ", ".join(issue.code for issue in result.errors)
        super().__init__(f"Job validation failed: {codes}.")


class InvalidJobTransitionError(PublisherDomainError):
    """Raised when a publisher job status transition is not permitted."""
