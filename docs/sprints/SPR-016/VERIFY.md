# SPR-016 Verification Plan

Status: planned, not executed. New package/tests/example do not exist at baseline.

After future implementation, install .[dev] and run:

~~~sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest tests/docx_pipeline/test_docx_publication.py tests/publishing/test_docx.py
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pytest tests/docx_pipeline --cov=bgdxpublisher.docx_pipeline --cov-report=term-missing --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
~~~

Also run all six existing independent >=95% commands for domain, jobs, pipeline,
orchestration, html_pipeline and batch_pipeline exactly as in ci.yml. No threshold
may be reduced. Run Ubuntu/Windows Python 3.13/3.14; document skips and execute
filesystem cases on Linux.

## Test sequence

1. Prove stage contracts, one read/render/write, independent jobs/contexts and
   immutable result/error consistency. Forbid legacy publish fallback.
2. Generate legacy/new DOCX using identical inputs; compare OOXML members and
   semantics per IMPLEMENTATION-SPEC, not raw ZIP bytes. Include default/custom
   metadata, UTF-8/BOM, empty/complex Markdown, lists, links and image safety.
3. Inject validation/read/render/commit/cleanup failures, aliases, overwrite races
   and symlinks; assert stage/cause, source/output bytes, temp cleanup and no rollback.
4. Capture logs with sentinel paths/title/body/raw causes. Verify new runtime
   registration and explicit CLI legacy-selection spy; preserve existing CLI tests.
5. Build/install wheel in fresh venv. Copy proposed examples/docx_pipeline.py to
   another directory outside checkout, clear source PYTHONPATH, confirm site-packages
   imports, then run API success/refusal/overwrite/failure checks and inspect OOXML.
6. Keep existing real publish-docx CLI smoke and visual sample generation. Open
   generated DOCX PDF/page artifacts, review layout and Unicode, and record exact
   artifact/run/SHA; successful conversion alone is not visual review.
7. Review source and four CI jobs. Only after separate merge authorization, inspect
   exact merge-SHA CI and record acceptance/closure before closing future issue.

Record actual output, dependencies and normalization decisions. Do not copy
SPR-015 test counts as SPR-016 evidence or mark plan commands as executed.
