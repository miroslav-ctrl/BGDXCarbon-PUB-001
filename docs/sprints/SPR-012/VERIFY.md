# SPR-012 Verification

Status: verified and closed; see [local evidence](IMPLEMENTATION-EVIDENCE.md).
Four-platform CI, technical review and post-merge verification are complete; see [closure evidence](CLOSURE.md).

Use Python 3.13/3.14 and install .[dev]. Run Ruff, Black, MyPy and all regression tests.

```sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pytest tests/domain --cov=bgdxpublisher.domain --cov-fail-under=95
python -m pytest tests/jobs --cov=bgdxpublisher.jobs --cov-fail-under=95
python -m pytest tests/pipeline --cov=bgdxpublisher.pipeline --cov-fail-under=95
python -m pytest tests/orchestration --cov=bgdxpublisher.orchestration --cov-fail-under=95
python -m pytest tests/html_pipeline --cov=bgdxpublisher.html_pipeline --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
```

Install wheel into a fresh environment. Outside checkout, publish actual UTF-8/BOM Markdown through HtmlPublicationService; inspect result, HTML metadata/body and unchanged source. Exercise overwrite refusal and typed invalid-metadata failure. Compare output bytes against legacy PublishingService. Resolve the new service from runtime without changing the default coordinator. Add these checks to all four CI jobs.

Run failure injection before commit and after commit/cleanup; inspect both typed result and disk state. Preserve existing platform-specific filesystem tests. Record AC-01–AC-12 evidence and CI links; perform rendered HTML/browser comparison if equivalence tests expose a rendering difference. Close #25 only after review, authorized merge and successful exact merge SHA CI.
