# SPR-014 Verification

Status: implemented for review; see [local evidence](IMPLEMENTATION-EVIDENCE.md).
Four-platform CI, review and post-merge verification remain required.

Install .[dev] using Python 3.13/3.14, then run:

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
python -m pytest tests/batch_pipeline --cov=bgdxpublisher.batch_pipeline --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
```

Install wheel into a fresh environment and execute the Python API example outside checkout. Verify two successful documents and optional index, then invalid UTF-8 mixed with valid source and an independent index overwrite failure. Inspect typed item outcomes, index links, unchanged sources and retained outputs. Include requested index with zero successful items.

Use integration failure injection for alias/symlink/race and postcommit cleanup cases; ensure failed-but-committed items are excluded from index. Confirm existing publish-batch CLI still uses legacy route and all other commands retain behavior.

Map evidence to AC-01–AC-12. All four CI combinations must pass. Record exact merge SHA and post-merge run links after review/authorized merge before closing #31.
