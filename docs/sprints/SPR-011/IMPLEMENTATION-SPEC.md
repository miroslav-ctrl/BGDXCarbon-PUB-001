# SPR-011 Implementation Specification

## Existing components

src/bgdxpublisher/jobs/service.py creates immutable jobs and delegates transitions to JobLifecycle. src/bgdxpublisher/pipeline/engine.py validates and executes sequential stages and closes context. src/bgdxpublisher/runtime/application.py composes services. Reuse these boundaries; do not duplicate transition or cleanup algorithms.

## Public API

New package bgdxpublisher.orchestration exports JobExecutionService, JobExecutionResult, JobExecutionError and JobExecutionStateError.

Proposed constructor:
`JobExecutionService(job_service: JobService, pipeline: PipelineEngine, logger: Logger | None = None)`.

Proposed call:
`execute(job: PublisherJob, value: object) -> JobExecutionResult`.

JobExecutionResult is a frozen, slotted envelope containing final_job: PublisherJob, pipeline_result: PipelineResult and status_history: tuple[JobStatus, ...]. Success requires a COMPLETED job, a COMPLETED pipeline result and history (QUEUED, RUNNING, COMPLETED). It must reject inconsistent combinations. Freezing the envelope does not promise deep immutability of arbitrary pipeline output objects.

JobExecutionStateError rejects a job whose status is not QUEUED, before context creation, transitions or stage execution. It retains the original job and exposes a stable JOB_EXECUTION_STATE_INVALID code. Do not fabricate a FAILED transition for an already terminal job.

JobExecutionError carries a frozen failure result with final_job FAILED, pipeline_result FAILED and history (QUEUED, RUNNING, FAILED). Preserve PipelineExecutionError as __cause__, retaining its original stage cause chain. Reuse PipelineFailure fields and do not expose partial output. Use a stable JOB_EXECUTION_FAILED coordinator code; stage-specific codes remain in pipeline_result.failure.

## Execution algorithm

1. Validate QUEUED precondition; preserve caller job unchanged.
2. Transition to a new RUNNING job through injected JobService.
3. Create PipelineContext(job=running_job) for this call only.
4. Execute the injected engine with value and context.
5. On success, transition RUNNING to COMPLETED and return the success envelope.
6. On PipelineExecutionError, transition RUNNING to FAILED and raise JobExecutionError from the pipeline error with the failure envelope.

PipelineEngine owns context closure. The coordinator must not close it again. A cleanup failure is an execution failure, so COMPLETED must occur only after engine success. An empty pipeline follows the same lifecycle and returns the input value.

Unexpected dependency/programming errors must propagate without being silently converted into successful results. This sprint guarantees failure envelopes for the existing typed pipeline execution failure paths; it does not promise recovery from arbitrary corrupted injected dependencies.

## Ownership and logging

The service holds configuration/dependencies only; no last-job, last-context or last-result state. Every execute call creates its own context. It provides no cross-call deduplication or exactly-once guarantee: resubmitting the same immutable QUEUED snapshot is a distinct execution.

Pass the RUNNING job to stages for consistent job_id correlation. Log identifiers, status, stage names and stable codes only. Never log values, document content or raw exception messages in coordinator logs. Existing publishing logs are outside this sprint.

## Runtime composition

Register JobService and JobExecutionService with the existing runtime logger. Register an explicit empty default PipelineEngine as the no-op foundation; callers needing stages construct and inject their own engine/coordinator. Do not add a mutable global stage registry or configuration-driven plugin discovery. Integration tests resolve the default coordinator and demonstrate empty-pipeline execution.

## Verification and compatibility

Add tests under tests/orchestration and runtime integration tests. Add an independent >=95% bgdxpublisher.orchestration coverage command to CI, preserving total >=99% and individual domain/jobs/pipeline >=95% gates. Keep all four OS/Python combinations and installed-wheel checks.

Existing request/result contracts, CLI exit codes, default metadata, overwrite behavior, source preservation and publishing output remain compatible. No new external effects are added by orchestration itself; injected stages remain responsible for their own effects.
