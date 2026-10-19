# SPR-017 Verification Plan

Status: implemented for review. Commands below reproduce checks; actual local results are in IMPLEMENTATION-EVIDENCE.md. Runtime precedence tests also live in tests/cli/test_docx_runtime_precedence.py.

Install .[dev] and run:

~~~sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest tests/cli/test_docx_cli_pipeline.py tests/publishing/test_docx.py tests/docx_pipeline/test_docx_publication.py
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pip wheel . --no-deps --wheel-dir dist-review
~~~

Keep all seven independent >=95% commands in ci.yml for domain, jobs, pipeline,
orchestration, html_pipeline, batch_pipeline and docx_pipeline. No threshold
reduction/new dependency. Run Ubuntu/Windows Python 3.13/3.14; record skips and
execute filesystem cases on Linux.

## Verification sequence

1. Capture registered DocxPublicationService selection and exact DocxRequest;
   forbid legacy DOCX fallback. Verify direct PDF-first dispatch with both flags.
2. Differential OOXML comparison with legacy under identical dependencies; inspect
   package member sets and contents, not ZIP bytes. Check source bytes/metadata.
3. Assert exact primary stderr/stdout/exit contracts and parser-before-runtime
   rejection. Inject validate/read/render/write/cleanup and safe sentinel causes.
4. Inject runtime initialize/start/stop errors; combine primary DOCX failure and
   expected stop error; assert cleanup-before-primary line ordering and one primary.
   Test unexpected DOCX failure plus unexpected stop without masking primary,
   as well as unexpected stop without primary.
5. Verify refusal/overwrite/alias/symlink/race/precommit and postcommit preservation.
   Retain direct API tests; update only CLI route/text assertions intentionally.
6. Build/install wheel in fresh venv. Run actual publish-docx executable outside
   checkout with source PYTHONPATH removed; success/refusal/overwrite, invalid
   metadata (exit 2) and missing/invalid UTF-8 source (safe exit 1). Retain copied
   DOCX API smoke and other CLI checks.
7. Retain CI DOCX visual sample generation and actually open its PDF/page artifact
   on the tested SHA; review Unicode/layout and record artifact/run/page.
8. Source review and four CI jobs precede separately authorized merge. Verify exact
   merge SHA/CI and acceptance/closure before closing future implementation issue.

Do not report planned commands or prior SPR-016 counts as SPR-017 executed evidence.
