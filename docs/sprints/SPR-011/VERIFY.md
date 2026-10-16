# SPR-011 Verification

Status: implemented for review. See [local evidence](IMPLEMENTATION-EVIDENCE.md).
Four-platform CI and post-merge evidence must be recorded separately.

Use Python 3.13 or 3.14, install .[dev], then run from the repository:

```sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pytest tests/domain --cov=bgdxpublisher.domain --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/jobs --cov=bgdxpublisher.jobs --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/pipeline --cov=bgdxpublisher.pipeline --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/orchestration --cov=bgdxpublisher.orchestration --cov-report=term-missing --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
```

In a fresh environment install the built wheel and run outside the repository. Create a valid Document and JobRequest; use JobService to reach VALIDATED then QUEUED. Construct a typed integer stage, run JobExecutionService and assert output, final status, preserved input job and history. Repeat with a failing stage; assert JobExecutionError, FAILED job, absent partial output and cause chain. Resolve the default coordinator from initialized runtime and verify empty-pipeline behavior.

Map results to AC-01 through AC-13 in ACCEPTANCE.md. CI must execute Windows/Linux × Python 3.13/3.14 with independent coverage gates. Save run links, exact head/merge SHA and relevant logs. Confirm post-merge CI before closing #22. Existing publishing visual acceptance is not repeated unless implementation changes rendering.
