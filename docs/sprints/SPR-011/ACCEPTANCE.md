# SPR-011 Acceptance Criteria

AC-01–AC-13 verified on merge 4baf1e99; see [closure evidence](CLOSURE.md) and implementation mapping.

| ID | Criterion | Required evidence |
| --- | --- | --- |
| AC-01 | QUEUED job executes stages in declared order and returns COMPLETED only after cleanup | Integration test and exact history QUEUED, RUNNING, COMPLETED |
| AC-02 | Original job is unchanged; result/history envelopes reject mutation and inconsistent states | Contract tests; arbitrary output is not claimed deeply immutable |
| AC-03 | CREATED, VALIDATED, RUNNING, COMPLETED and FAILED inputs are rejected before stages or transitions | Parameterized tests, JOB_EXECUTION_STATE_INVALID, original job retained |
| AC-04 | Stage, input and output failures produce FAILED job and no partial output | JobExecutionError, stable code, original cause chain, completed-stage details |
| AC-05 | Cleanup failure produces FAILED; cleanup runs once in reverse order and all cleanup failures remain available | Stage spies and existing PipelineFailure cleanup details |
| AC-06 | Empty pipeline completes and returns the input unchanged | Service and runtime default integration tests |
| AC-07 | Independent calls have fresh contexts, stable per-run job_id and no retained execution state | Context capture tests with separate jobs, repeated calls and failures |
| AC-08 | Coordinator logs contain identifiers/codes without input or exception content | Captured logs with secret sentinel values |
| AC-09 | Runtime registers dependencies and closes normally after success/failure | Runtime integration tests; no global mutable registry |
| AC-10 | Installed wheel exposes the API outside source checkout | CI smoke: valid job progression to QUEUED, success and typed stage failure |
| AC-11 | Existing publishing/CLI behavior remains compatible | Full regression suite and existing wheel checks |
| AC-12 | Quality gates pass in all four CI combinations | Ruff, Black, MyPy, total coverage >=99%; domain/jobs/pipeline/orchestration each >=95% |
| AC-13 | Delivery and closure are traceable | Reviewed implementation PR to develop, successful post-merge CI SHA and closure evidence |

No acceptance box may be marked complete based solely on this planning PR.
