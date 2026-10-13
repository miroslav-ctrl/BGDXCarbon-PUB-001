"""Immutable publisher job models and request validation."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from bgdxpublisher.domain import Document, ValidationIssue, ValidationResult

from .exceptions import JobValidationError


class JobStatus(str, Enum):
    """Supported lifecycle states of a publisher job."""

    CREATED = "created"
    VALIDATED = "validated"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class JobRequest:
    """Untrusted input used to create a publisher job."""

    document: object
    job_id: object = None
    created_at: object = None


@dataclass(frozen=True, slots=True)
class PublisherJob:
    """Immutable job identity, document association, and status."""

    document_id: str
    job_id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.CREATED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate identifiers and normalize the creation timestamp to UTC."""
        issues: list[ValidationIssue] = []
        try:
            normalized_document_id = str(UUID(self.document_id))
        except (ValueError, TypeError, AttributeError):
            normalized_document_id = ""
            issues.append(
                ValidationIssue(
                    "JOB_DOCUMENT_ID_INVALID",
                    "document_id",
                    "Document identifier must be a UUID.",
                )
            )
        try:
            normalized_job_id = str(UUID(self.job_id))
        except (ValueError, TypeError, AttributeError):
            normalized_job_id = ""
            issues.append(
                ValidationIssue(
                    "JOB_ID_INVALID", "job_id", "Job identifier must be a UUID."
                )
            )
        if not isinstance(self.status, JobStatus):
            issues.append(
                ValidationIssue(
                    "JOB_STATUS_INVALID", "status", "Job status is unsupported."
                )
            )
        if (
            not isinstance(self.created_at, datetime)
            or self.created_at.utcoffset() is None
        ):
            issues.append(
                ValidationIssue(
                    "JOB_CREATED_AT_INVALID",
                    "created_at",
                    "Creation timestamp must be timezone-aware.",
                )
            )
        if issues:
            raise JobValidationError(ValidationResult(tuple(issues)))
        object.__setattr__(self, "document_id", normalized_document_id)
        object.__setattr__(self, "job_id", normalized_job_id)
        object.__setattr__(self, "created_at", self.created_at.astimezone(timezone.utc))


def validate_job_request(request: JobRequest) -> ValidationResult:
    """Validate a job request before lifecycle or pipeline execution."""
    issues: list[ValidationIssue] = []
    if not isinstance(request.document, Document):
        issues.append(
            ValidationIssue(
                "JOB_DOCUMENT_REQUIRED",
                "document",
                "A validated document is required.",
            )
        )
    if request.job_id is not None:
        try:
            UUID(str(request.job_id))
        except (ValueError, TypeError, AttributeError):
            issues.append(
                ValidationIssue(
                    "JOB_ID_INVALID", "job_id", "Job identifier must be a UUID."
                )
            )
    if request.created_at is not None and (
        not isinstance(request.created_at, datetime)
        or request.created_at.utcoffset() is None
    ):
        issues.append(
            ValidationIssue(
                "JOB_CREATED_AT_INVALID",
                "created_at",
                "Creation timestamp must be timezone-aware.",
            )
        )
    return ValidationResult(tuple(issues))
