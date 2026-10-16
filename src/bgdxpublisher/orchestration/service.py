"""Coordinate immutable job transitions around an engine-owned pipeline run."""

from dataclasses import dataclass
from logging import Logger

from bgdxpublisher.domain import PublisherDomainError
from bgdxpublisher.jobs import JobService, JobStatus, PublisherJob
from bgdxpublisher.pipeline import (
    PipelineContext,
    PipelineEngine,
    PipelineExecutionError,
    PipelineResult,
    PipelineStatus,
)


@dataclass(frozen=True, slots=True)
class JobExecutionResult:
    """Consistent terminal job and pipeline snapshots for one execution."""

    final_job: PublisherJob
    pipeline_result: PipelineResult
    status_history: tuple[JobStatus, ...]

    def __post_init__(self) -> None:
        """Reject nonterminal or mismatched result envelopes."""
        terminal = (
            JobStatus.COMPLETED
            if self.pipeline_result.status is PipelineStatus.COMPLETED
            else JobStatus.FAILED
        )
        if self.final_job.status is not terminal or self.status_history != (
            JobStatus.QUEUED,
            JobStatus.RUNNING,
            terminal,
        ):
            raise ValueError("Job, pipeline and status history must agree.")
        object.__setattr__(self, "status_history", tuple(self.status_history))


class JobExecutionStateError(PublisherDomainError):
    """Reject an execution without changing the submitted job."""

    code = "JOB_EXECUTION_STATE_INVALID"

    def __init__(self, job: PublisherJob) -> None:
        """Retain the rejected immutable job."""
        self.job = job
        super().__init__(self.code)


class JobExecutionError(PublisherDomainError):
    """Expose a failed execution without input or exception content."""

    code = "JOB_EXECUTION_FAILED"

    def __init__(self, result: JobExecutionResult) -> None:
        """Retain only a consistent failed result."""
        if result.final_job.status is not JobStatus.FAILED:
            raise ValueError("JobExecutionError requires a failed result.")
        self.result = result
        super().__init__(self.code)


class JobExecutionService:
    """Execute QUEUED jobs synchronously with fresh per-call contexts."""

    def __init__(
        self,
        job_service: JobService,
        pipeline: PipelineEngine,
        logger: Logger | None = None,
    ) -> None:
        """Use explicit dependencies without retaining execution state."""
        self._jobs = job_service
        self._pipeline = pipeline
        self._logger = logger

    def execute(self, job: PublisherJob, value: object) -> JobExecutionResult:
        """Return a completed execution or raise a typed state/pipeline error."""
        if job.status is not JobStatus.QUEUED:
            raise JobExecutionStateError(job)
        running = self._jobs.transition(job, JobStatus.RUNNING)
        context = PipelineContext(job=running)
        try:
            result = self._pipeline.execute(value, context)
        except PipelineExecutionError as error:
            failed = self._jobs.transition(running, JobStatus.FAILED)
            failure = JobExecutionResult(
                failed,
                error.result,
                (JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.FAILED),
            )
            self._log(failed, JobExecutionError.code)
            raise JobExecutionError(failure) from error
        completed = self._jobs.transition(running, JobStatus.COMPLETED)
        self._log(completed, "JOB_EXECUTION_COMPLETED")
        return JobExecutionResult(
            completed,
            result,
            (JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.COMPLETED),
        )

    def _log(self, job: PublisherJob, code: str) -> None:
        """Log identifiers and codes only."""
        if self._logger is not None:
            self._logger.info(
                "Job execution job_id=%s status=%s code=%s",
                job.job_id,
                job.status.value,
                code,
            )
