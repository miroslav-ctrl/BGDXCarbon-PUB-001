"""Typed publisher domain exceptions."""

from bgdxpublisher.exceptions import RuntimeFoundationError

from .validation import ValidationResult


class PublisherDomainError(RuntimeFoundationError):
    """Base class for publisher document, job, and pipeline errors."""


class DocumentValidationError(PublisherDomainError):
    """Raised when a document request contains validation errors."""

    def __init__(self, result: ValidationResult) -> None:
        """Create an error retaining stable structured validation issues."""
        self.result = result
        codes = ", ".join(issue.code for issue in result.errors)
        super().__init__(f"Document validation failed: {codes}.")
