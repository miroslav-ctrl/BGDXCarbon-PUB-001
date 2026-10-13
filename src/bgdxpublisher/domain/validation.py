"""Structured validation results shared by publisher domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Describe one stable, field-specific validation error."""

    code: str
    field: str
    message: str


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Collect validation errors without exposing invalid input values."""

    errors: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        """Return whether validation completed without errors."""
        return not self.errors

    def extend(self, other: ValidationResult) -> ValidationResult:
        """Return a result containing errors from both validations."""
        return ValidationResult(self.errors + other.errors)
