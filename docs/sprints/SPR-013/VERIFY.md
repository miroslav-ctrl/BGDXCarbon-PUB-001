# SPR-013 Verification

Status: verified and closed; see [local evidence](IMPLEMENTATION-EVIDENCE.md).
Four-platform CI, technical review and post-merge verification are complete; see [closure evidence](CLOSURE.md).

Install .[dev] on Python 3.13/3.14, then run:

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

Install the wheel into a fresh environment and execute CLI outside checkout. Publish UTF-8/BOM Serbian text using default options and custom title/lang/theme/TOC; verify file bytes and Published output. Repeat without overwrite: exit 1, stable HTML_PUBLICATION_FAILED stage=validate and unchanged output. Explicit overwrite succeeds. Invalid lang en_US exits 2 before publication. Missing source exits 1 with stage=validate and no raw cause message.

Test read/render/write/cleanup failures by injection in the integration suite. Test shutdown failure after success and alongside primary publication failure; inspect stdout/stderr, runtime stop and disk state. Retain all existing DOCX/PDF/batch tests and wheel checks.

Map results to AC-01–AC-10. Run all four CI combinations, save exact head/merge SHA and run links, and close #28 only after review, authorized merge and successful post-merge verification.
