"""Installed-wheel example: execute a queued job and inspect a typed failure."""

from bgdxpublisher.domain import Document, DocumentType
from bgdxpublisher.jobs import JobRequest, JobService, JobStatus
from bgdxpublisher.orchestration import JobExecutionError, JobExecutionService
from bgdxpublisher.pipeline import PipelineContext, PipelineEngine


class IntegerStage:
    """Increment an integer with explicit pipeline contracts."""

    name = "increment"
    input_type = int
    output_type = int

    def execute(self, value: object, context: PipelineContext) -> object:
        """Return an incremented value."""
        assert isinstance(value, int)
        return value + 1


class FailingStage(IntegerStage):
    """Demonstrate typed pipeline failure propagation."""

    def execute(self, value: object, context: PipelineContext) -> object:
        """Raise an example stage error."""
        raise RuntimeError("example failure")


def main() -> None:
    """Verify success and failure without filesystem publishing."""
    jobs = JobService()
    document = Document(DocumentType.MARKDOWN, "Example", "example.md")
    job = jobs.create_job(JobRequest(document))
    for status in (JobStatus.VALIDATED, JobStatus.QUEUED):
        job = jobs.transition(job, status)
    result = JobExecutionService(jobs, PipelineEngine((IntegerStage(),))).execute(
        job, 1
    )
    assert result.final_job.status is JobStatus.COMPLETED
    assert result.pipeline_result.output == 2
    assert result.status_history == (
        JobStatus.QUEUED,
        JobStatus.RUNNING,
        JobStatus.COMPLETED,
    )
    assert job.status is JobStatus.QUEUED
    try:
        JobExecutionService(jobs, PipelineEngine((FailingStage(),))).execute(job, 1)
    except JobExecutionError as error:
        assert error.result.final_job.status is JobStatus.FAILED
        assert error.result.pipeline_result.output is None
        assert error.__cause__ is not None
        assert isinstance(error.__cause__.__cause__, RuntimeError)
    else:
        raise AssertionError("Expected JobExecutionError")


if __name__ == "__main__":
    main()
