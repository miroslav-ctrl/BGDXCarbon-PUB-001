"""Publisher job request validation and lifecycle service."""

from datetime import datetime, timezone
from logging import Logger
from typing import cast
from uuid import uuid4

from bgdxpublisher.domain import Document, ValidationResult

from .exceptions import JobValidationError
from .lifecycle import JobLifecycle
from .models import JobRequest, JobStatus, PublisherJob, validate_job_request


class JobService:
    """Create jobs and coordinate their immutable lifecycle transitions."""

    def __init__(
        self,
        lifecycle: JobLifecycle | None = None,
        logger: Logger | None = None,
    ) -> None:
        """Create a job service with an optional existing application logger."""
        self._lifecycle = lifecycle or JobLifecycle()
        self._logger = logger

    def validate_request(self, request: JobRequest) -> ValidationResult:
        """Return structured validation errors for a job request."""
        return validate_job_request(request)

    def create_job(self, request: JobRequest) -> PublisherJob:
        """Create a job only after validating the associated document request."""
        result = self.validate_request(request)
        if not result.is_valid:
            raise JobValidationError(result)
        document = cast(Document, request.document)
        job = PublisherJob(
            document_id=document.document_id,
            job_id=str(request.job_id) if request.job_id is not None else str(uuid4()),
            created_at=(
                cast(datetime, request.created_at)
                if request.created_at is not None
                else datetime.now(timezone.utc)
            ),
        )
        if self._logger is not None:
            self._logger.info("Publisher job created job_id=%s", job.job_id)
        return job

    def transition(self, job: PublisherJob, status: JobStatus) -> PublisherJob:
        """Transition a job and log its identifier and resulting state."""
        updated = self._lifecycle.transition(job, status)
        if self._logger is not None:
            self._logger.info(
                "Publisher job transitioned job_id=%s status=%s",
                updated.job_id,
                updated.status.value,
            )
        return updated
