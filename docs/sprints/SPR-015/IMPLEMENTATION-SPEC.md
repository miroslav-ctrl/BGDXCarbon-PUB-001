# SPR-015 Implementation Specification

Status: proposed; no implementation.

## Routing

Keep run_batch signature and app.py parser unchanged, including positional source, required --output-dir, --overwrite, --config, --lang, --theme, --toc and --index defaults. Initialize/start PublisherApplication once. Resolve BatchHtmlPublicationService from context.services and call publish once with BatchRequest(source, output, overwrite, language, theme, toc, index). No fallback to legacy publish_batch or duplicate publication. Legacy direct publish_batch API and result/exception contracts remain unchanged.

## Outcome projection and stdout

Project items in service-provided deterministic order. A published item is one whose execution.final_job.status is COMPLETED; every FAILED item counts as failed, including cleanup failure after commit. Count documents only in the summary; index failures do not increase the document failure count.

For each COMPLETED item: Published: <output path> plus newline.
Then: Batch complete: <completed count> published, <failed count> failed. plus newline.
If index succeeded: Index published: <index output path> plus newline.
No job IDs, pipeline metadata or extra success lines. Index disabled produces no index line.
All-failed documents may still yield a valid empty index and exit 1.

## Proposed expected stderr

- Batch preflight: Batch publication failed: BATCH_HTML_PREFLIGHT_FAILED
- Per-item failure: Failed: item=<1-based discovery ordinal> HTML_PUBLICATION_FAILED stage=<stage>
- Independent index failure: Index publication failed: BATCH_INDEX_FAILED

One newline per diagnostic; no raw exception/cause messages, document content, title, source/output path or traceback in these new publication diagnostics. Read the per-item stage from structured pipeline_result.failure, not by parsing strings. Index exception_type is not printed. Ordinal identifies an item without exposing source filenames. Successful stdout retains requested output paths, as before.

Parser diagnostics remain precise and exit 2 before runtime publication. Expected preflight/item/index failures exit 1. Full successful publication/index and successful shutdown exit 0. Preserve existing RuntimeFoundationError handling for initialization/start failures; do not expand this sprint into changing all runtime/config diagnostics. Runtime cleanup keeps its existing prefix. Unexpected programming exceptions propagate after finally cleanup, without conversion to success or a fabricated batch result.

## Runtime shutdown and output timing

Buffer item/index/summary output until publication and runtime shutdown have been attempted. Stop CONFIGURED/RUNNING runtime in finally; do not stop CREATED runtime. On expected shutdown failure, exit 1 and suppress all buffered stdout success/summary lines, retaining any structured publication diagnostics and the Runtime cleanup failed diagnostic. A primary publication failure must not be replaced by shutdown failure. If an unexpected exception is active, shutdown handling must not swallow it.

No deletion, rollback or restoration of committed files. An item cleanup failure remains FAILED and excluded from index even if its output file exists. Independent index failure preserves committed documents.

## Compatibility and tests

Retain single HTML publish, DOCX/PDF, no-argument runtime and configuration command behavior. Reuse SPR-014 discovery, collisions, aliases, symlinks, race guards, escaping and atomic writer. Avoid touching engine contracts merely to adapt CLI output.

Existing tests/cli/test_batch.py currently assert source filenames in stderr; test_batch_index.py asserts raw Output exists / disk error. Update only CLI-facing expectations to stable codes/ordinals. Keep legacy direct API assertions and coverage intact. Add tests in tests/cli/test_batch_pipeline.py (proposed path) with forbidden legacy-call spies, captured BatchRequest, failure/cleanup injection and repeated invocations. Verify no Markdown/path/sentinel leakage in new route logs/stderr.

CI stays Ubuntu/Windows × Python 3.13/3.14, total coverage >=99% and all six existing package thresholds >=95%; no threshold reduction. Extend the existing fresh-wheel outside-checkout step for real publish-batch success, partial failure, preflight failure, independent index failure and overwrite. Use a copied Python smoke script for deterministic index-failure injection against installed code, without changing production APIs for testing.
