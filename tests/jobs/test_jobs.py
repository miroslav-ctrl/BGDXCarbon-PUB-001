"""Tests for publisher job creation, validation, and lifecycle transitions."""

import logging
from dataclasses import FrozenInstanceError
from datetime import datetime
from uuid import uuid4

import pytest

from bgdxpublisher.domain import Document, DocumentType
from bgdxpublisher.jobs import (
    InvalidJobTransitionError,
    JobRequest,
    JobService,
    JobStatus,
    JobValidationError,
    PublisherJob,
    validate_job_request,
)


def _document() -> Document:
    return Document(DocumentType.MARKDOWN, "Title", "source.md")


def test_job_service_creates_immutable_created_job() -> None:
    service = JobService()
    document = _document()
    requested_id = str(uuid4())

    job = service.create_job(JobRequest(document, job_id=requested_id))

    assert job.document_id == document.document_id
    assert job.job_id == requested_id
    assert job.status is JobStatus.CREATED
    with pytest.raises(FrozenInstanceError):
        job.status = JobStatus.RUNNING  # type: ignore[misc]


def test_job_transitions_follow_the_required_sequence() -> None:
    service = JobService()
    job = service.create_job(JobRequest(_document()))

    for state in (
        JobStatus.VALIDATED,
        JobStatus.QUEUED,
        JobStatus.RUNNING,
        JobStatus.COMPLETED,
    ):
        job = service.transition(job, state)
        assert job.status is state


@pytest.mark.parametrize(
    "state",
    [JobStatus.CREATED, JobStatus.VALIDATED, JobStatus.QUEUED, JobStatus.RUNNING],
)
def test_failure_is_permitted_before_terminal_states(state: JobStatus) -> None:
    service = JobService()
    job = service.create_job(JobRequest(_document()))
    transitions = {
        JobStatus.CREATED: (),
        JobStatus.VALIDATED: (JobStatus.VALIDATED,),
        JobStatus.QUEUED: (JobStatus.VALIDATED, JobStatus.QUEUED),
        JobStatus.RUNNING: (
            JobStatus.VALIDATED,
            JobStatus.QUEUED,
            JobStatus.RUNNING,
        ),
    }

    for intermediate in transitions[state]:
        job = service.transition(job, intermediate)
    assert service.transition(job, JobStatus.FAILED).status is JobStatus.FAILED


@pytest.mark.parametrize(
    ("state", "target"),
    [
        (JobStatus.CREATED, JobStatus.RUNNING),
        (JobStatus.COMPLETED, JobStatus.FAILED),
        (JobStatus.FAILED, JobStatus.RUNNING),
        (JobStatus.RUNNING, JobStatus.VALIDATED),
    ],
)
def test_forbidden_job_transitions_raise_typed_error(
    state: JobStatus, target: JobStatus
) -> None:
    job = PublisherJob(document_id=str(uuid4()), status=state)

    with pytest.raises(InvalidJobTransitionError):
        JobService().transition(job, target)


def test_non_enum_job_transition_target_raises_typed_error() -> None:
    job = JobService().create_job(JobRequest(_document()))

    with pytest.raises(InvalidJobTransitionError, match="Unsupported target"):
        JobService().transition(job, "invalid")  # type: ignore[arg-type]


def test_job_request_validation_returns_structured_errors() -> None:
    request = JobRequest(
        document=object(),
        job_id="bad-id",
        created_at=datetime(2026, 1, 1),
    )

    result = validate_job_request(request)

    assert not result.is_valid
    assert {issue.code for issue in result.errors} == {
        "JOB_DOCUMENT_REQUIRED",
        "JOB_ID_INVALID",
        "JOB_CREATED_AT_INVALID",
    }
    with pytest.raises(JobValidationError) as error:
        JobService().create_job(request)
    assert error.value.result == result


def test_direct_job_model_rejects_invalid_identifiers() -> None:
    with pytest.raises(JobValidationError) as document_error:
        PublisherJob(document_id="invalid")
    assert document_error.value.result.errors[0].code == "JOB_DOCUMENT_ID_INVALID"

    with pytest.raises(JobValidationError) as error:
        PublisherJob(
            document_id=str(uuid4()),
            job_id="invalid",
            status="unsupported",  # type: ignore[arg-type]
            created_at=datetime(2026, 1, 1),
        )

    assert {issue.code for issue in error.value.result.errors} == {
        "JOB_ID_INVALID",
        "JOB_STATUS_INVALID",
        "JOB_CREATED_AT_INVALID",
    }


def test_job_service_logs_only_job_identifiers(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = logging.getLogger("bgdxpublisher.test.jobs")
    caplog.set_level(logging.INFO, logger=logger.name)
    job = JobService(logger=logger).create_job(JobRequest(_document()))
    JobService(logger=logger).transition(job, JobStatus.VALIDATED)

    assert job.job_id in caplog.text
    assert "Title" not in caplog.text
    assert "source.md" not in caplog.text
