"""Execution contracts, cleanup ownership and runtime composition."""

import logging
from dataclasses import FrozenInstanceError, dataclass, replace
from uuid import uuid4

import pytest

from bgdxpublisher.jobs import JobService, JobStatus, PublisherJob
from bgdxpublisher.orchestration import (
    JobExecutionError,
    JobExecutionService,
    JobExecutionStateError,
)
from bgdxpublisher.pipeline import (
    PipelineContext,
    PipelineEngine,
    PipelineExecutionError,
    PipelineResult,
    PipelineStatus,
)
from bgdxpublisher.runtime import PublisherApplication, RuntimeState


def queued() -> PublisherJob:
    return PublisherJob(document_id=str(uuid4()), status=JobStatus.QUEUED)


@dataclass
class Stage:
    name: str = "stage"
    input_type: type = int
    output_type: type = int
    mode: str = "success"

    def execute(self, value: object, context: PipelineContext) -> object:
        assert context.job is not None
        assert context.job.status is JobStatus.RUNNING
        if self.mode == "fail":
            raise RuntimeError("secret-sentinel")
        if self.mode == "output":
            return "wrong"
        return value


def test_success_order_snapshots_and_cleanup_before_completion() -> None:
    events = []

    class ObservedJobs(JobService):
        def transition(self, job, status):
            events.append(status)
            return super().transition(job, status)

    class ObservedStage(Stage):
        def execute(self, value, context):
            events.append(self.name)
            context.register_cleanup(lambda: events.append("cleanup-" + self.name))
            return super().execute(value, context)

    job = queued()
    result = JobExecutionService(
        ObservedJobs(), PipelineEngine((ObservedStage("first"), ObservedStage("last")))
    ).execute(job, 3)
    assert events == [
        JobStatus.RUNNING,
        "first",
        "last",
        "cleanup-last",
        "cleanup-first",
        JobStatus.COMPLETED,
    ]
    assert job.status is JobStatus.QUEUED
    assert result.final_job.job_id == job.job_id
    assert result.final_job is not job
    assert result.pipeline_result.output == 3
    assert result.status_history == (
        JobStatus.QUEUED,
        JobStatus.RUNNING,
        JobStatus.COMPLETED,
    )
    with pytest.raises(FrozenInstanceError):
        result.final_job = job
    with pytest.raises(TypeError):
        result.status_history[0] = JobStatus.CREATED
    with pytest.raises(ValueError):
        replace(result, final_job=job)
    with pytest.raises(ValueError):
        replace(result, status_history=())
    with pytest.raises(ValueError):
        JobExecutionError(result)


@pytest.mark.parametrize("status", [s for s in JobStatus if s is not JobStatus.QUEUED])
def test_rejected_state_never_invokes_dependencies(status) -> None:
    class ForbiddenJobs(JobService):
        def transition(self, *args):
            pytest.fail("transition must not run")

    class ForbiddenEngine(PipelineEngine):
        def execute(self, *args):
            pytest.fail("engine must not run")

    job = replace(queued(), status=status)
    with pytest.raises(JobExecutionStateError) as error:
        JobExecutionService(ForbiddenJobs(), ForbiddenEngine()).execute(job, 1)
    assert error.value.job is job
    assert error.value.code == "JOB_EXECUTION_STATE_INVALID"


@pytest.mark.parametrize(
    "mode,value,code,cause",
    [
        ("fail", 1, "PIPELINE_STAGE_FAILED", RuntimeError),
        ("output", 1, "PIPELINE_OUTPUT_INVALID", Exception),
        ("success", "bad", "PIPELINE_INPUT_INVALID", Exception),
    ],
)
def test_typed_failures_preserve_causes_and_completed_stages(mode, value, code, cause):
    stages = (Stage("first"), Stage(mode=mode)) if mode != "success" else (Stage(),)
    job = queued()
    with pytest.raises(JobExecutionError) as error:
        JobExecutionService(JobService(), PipelineEngine(stages)).execute(job, value)
    result = error.value.result
    assert error.value.code == "JOB_EXECUTION_FAILED"
    assert result.final_job.status is JobStatus.FAILED
    assert result.final_job.job_id == job.job_id
    assert job.status is JobStatus.QUEUED
    assert result.status_history == (
        JobStatus.QUEUED,
        JobStatus.RUNNING,
        JobStatus.FAILED,
    )
    assert result.pipeline_result.output is None
    assert result.pipeline_result.completed_stages == (
        ("first",) if mode != "success" else ()
    )
    assert result.pipeline_result.failure.error_code == code
    assert isinstance(error.value.__cause__, PipelineExecutionError)
    assert isinstance(error.value.__cause__.__cause__, cause)
    with pytest.raises(ValueError):
        replace(result, final_job=replace(job, status=JobStatus.COMPLETED))


@pytest.mark.parametrize("stage_fails", [False, True])
def test_cleanup_errors_and_fresh_contexts(stage_fails) -> None:
    contexts = []
    cleaned = []

    class CleanupStage(Stage):
        def execute(self, value, context):
            contexts.append(context)

            def fail(label, error):
                cleaned.append(label)
                raise error("secret-sentinel")

            context.register_cleanup(lambda: fail("first", OSError))
            context.register_cleanup(lambda: fail("last", ValueError))
            if stage_fails:
                raise RuntimeError("secret-sentinel")
            return value

    service = JobExecutionService(JobService(), PipelineEngine((CleanupStage(),)))
    for job in (queued(), queued()):
        with pytest.raises(JobExecutionError) as error:
            service.execute(job, 1)
        failure = error.value.result.pipeline_result.failure
        assert failure.cleanup_exception_types == ("ValueError", "OSError")
        assert failure.error_code == (
            "PIPELINE_STAGE_FAILED" if stage_fails else "PIPELINE_CLEANUP_FAILED"
        )
        assert contexts[-1].job.job_id == job.job_id
        assert contexts[-1].close() == ()
    assert contexts[0] is not contexts[1]
    assert cleaned == ["last", "first", "last", "first"]


def test_empty_pipeline_and_safe_logs(caplog) -> None:
    logger = logging.getLogger("test.orchestration")
    caplog.set_level(logging.INFO, logger=logger.name)
    job = queued()
    value = {"secret-sentinel": True}
    service = JobExecutionService(JobService(), PipelineEngine(), logger)
    for _ in range(2):
        result = service.execute(job, value)
        assert result.pipeline_result.output is value
    with pytest.raises(JobExecutionError):
        JobExecutionService(
            JobService(), PipelineEngine((Stage(mode="fail"),)), logger
        ).execute(job, 1)
    assert job.job_id in caplog.text
    assert "JOB_EXECUTION_FAILED" in caplog.text
    assert "secret-sentinel" not in caplog.text


def test_unexpected_dependency_error_propagates() -> None:
    class BrokenEngine(PipelineEngine):
        def execute(self, *args):
            raise LookupError("broken dependency")

    with pytest.raises(LookupError):
        JobExecutionService(JobService(), BrokenEngine()).execute(queued(), 1)


def test_runtime_default_registration_and_shutdown() -> None:
    app = PublisherApplication()
    app.initialize()
    app.start()
    services = app.context.services
    jobs = services.resolve(JobService)
    assert isinstance(services.resolve(PipelineEngine), PipelineEngine)
    result = services.resolve(JobExecutionService).execute(queued(), 7)
    assert result.pipeline_result == PipelineResult(PipelineStatus.COMPLETED, 7, ())
    with pytest.raises(JobExecutionError):
        JobExecutionService(jobs, PipelineEngine((Stage(mode="fail"),))).execute(
            queued(), 1
        )
    app.stop()
    assert app.state is RuntimeState.STOPPED
