# SPR-021 Verification Plan

Status: planned checks; no implementation executed. Baseline CI39387903170
verifies existing develop, not future command existence/acceptance.

Proposed commands once implemented:

```sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest tests/cli/test_docx_batch_cli_pipeline.py tests/cli/test_docx_batch_runtime_precedence.py
python -m pytest tests/docx_batch_pipeline tests/docx_pipeline tests/publishing/test_docx.py tests/cli tests/runtime
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pytest tests/docx_batch_pipeline --cov=bgdxpublisher.docx_batch_pipeline --cov-report=term-missing --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
```

Retain/run ALL nine independent package gates in ci.yml; the command above shows
only relevant batch gate, not a replacement for the other eight.

1. Parser help/defaults/exact args/config/invalid lang/unsupported flags. Assert
   runtime constructor not called on parser errors/help; no old command drift.
2. Spy runtime factory/registered service/publish once/exact BatchDocxRequest;
   forbid fallback/single-service direct call by CLI. API is sole discovery owner.
3. Capture exact stream contents/count/order for all-completed/mixed/all-failed;
   case with first completed, second failed must report item=2. No index report.
4. Real service preflight (missing/file/empty/lang/root/candidate/dangling/alias/
   output symlink/directory/collision) -> exact safe line, no stdout; both overwrite
   modes, Linux filesystem cases, safe cause/name/path/content sentinel assertions.
   Existing regular output refusal remains per-item, later eligible item runs.
5. Invalid UTF-8/read, invalid filename-derived title/validate, injected render/
   write/fsync/replace/race/registered cleanup cases; previous/source bytes retained,
   no temporary leftovers for successful cleanup. Postcommit cleanup item FAILED/
   output None/file exists/later items run; no Published line for failed item.
6. Table-driven body states success/mixed/all/preflight/expected-runtime/unexpected
   crossed with stop success/expected-runtime/unexpected. Exact stderr order/count,
   stdout buffering/suppression, return vs propagation, primary identity and one
   fixed safe note (no stop content); already-handled typed failure is not active
   primary. CREATED/FAILED init no stop; CONFIGURED start failure stop once;
   RUNNING stop once. No file rollback. Existing HTML/DOCX/PDF command behavior
   is separately retained, not refactored to match new handler.
7. Differential CLI vs direct batch OOXML inventory/all uncompressed members,
   metadata/lang/Unicode/BOM/empty/different inputs; stable selection/order and
   index.md allowed, source unchanged. Preserve direct API diagnostic contracts.
8. Fresh temporary venv, copied example, clear PYTHONPATH, installed-import assertion;
   actual executable outside checkout (including --config). Success/refusal/
   overwrite/mixed/all/preflight/parser, safe per-item diagnostics. Isolated copied
   script for injected runtime checks; existing CLI/API wheel block retained.
9. Actual new CLI emits >=2 different DOCX outputs; retain/rasterize ALL pages,
   inspect layout/Unicode and record SHA/run/artifact/digest/pages. Retain existing
   batch API and single DOCX/PDF previews, no implied manual check from upload alone.
10. Exact-head four-job CI/static/full/nine gates, formal review and owner acceptance;
    separate merge authorization, exact post-merge CI and accepted closure before
    implementation issue completion. No release/tag/main modification.

Current planning checks: inspected cli/app.py, cli/batch.py, cli/publish.py,
SPR-020 API/spec/closure, SPR-015/019 error/lifecycle conventions, current CI and
release documentation. Documentation-only diff/link/UTF-8 checks and Draft plan
CI must be recorded separately from future implementation results.
