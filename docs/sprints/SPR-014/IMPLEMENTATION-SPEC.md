# SPR-014 Implementation Specification

## Public contracts

Add bgdxpublisher.batch_pipeline exporting BatchHtmlPublicationService, BatchHtmlPublicationResult, BatchHtmlItem and BatchHtmlPublicationError.

Proposed API: BatchHtmlPublicationService(logger: Logger).publish(request: BatchRequest) -> BatchHtmlPublicationResult. Inject or compose HtmlPublicationService; runtime registers the batch service alongside existing services. Do not replace the default empty coordinator or legacy publish_batch route.

BatchHtmlItem is a frozen slotted envelope with source: Path, output: Path and execution: JobExecutionResult. Completed execution must contain a PublishResult matching output. Failed execution must have no partial output. Retain original HtmlPublicationError in a private failure-handling path only as needed; aggregate public diagnostics use structured PipelineFailure, not str(error).

BatchHtmlPublicationResult is frozen and slotted, with items: tuple[BatchHtmlItem, ...], index: PublishResult | None and index_failure: BatchIndexFailure | None. Add frozen BatchIndexFailure with stable code BATCH_INDEX_FAILED and exception_type only. Index success and failure are mutually exclusive. Both absent means index disabled. Add an explicit index_requested: bool so requested-index outcomes cannot be confused with disabled index. Requested index requires exactly one success/failure outcome, even if every item failed.

BatchHtmlPublicationError represents batch preflight failure with stable BATCH_HTML_PREFLIGHT_FAILED code; preserve original cause with raise-from. No per-document job is fabricated for a preflight error.

## Preflight and ordering

Match existing nonrecursive selection: immediate regular files with suffix.lower() == '.md', ordered by (name.casefold(), name). Empty selections fail. Reject casefolded stem collisions and requested-index conflict with index.md before publishing any item.

Validate language/theme, source directory, output directory symlink policy and requested index output/overwrite/alias policy before item writes, following existing batch behavior. Preserve source/index/document alias checks. Create output directory only after these checks, retaining existing mkdir(parents=True, exist_ok=True) semantics; preflight failure is not a transaction rollback promise for filesystem metadata.

Reuse shared helpers only where needed and preserve legacy publish_batch exceptions/results. Preflight does not read Markdown bodies, render or publish. Item-level invalid source/output conditions remain item failures where legacy behavior allows independent attempts.

## Per-item execution

For each discovered source, construct PublishRequest with shared overwrite/language/theme/TOC and title=None, then call HtmlPublicationService once. Retain its job result as a BatchHtmlItem. Catch HtmlPublicationError to record FAILED and continue; successful items retain COMPLETED execution. Each call has independent document/job/context IDs. No aggregate queue or batch job lifecycle is introduced.

Unexpected programming exceptions propagate; do not silently turn arbitrary exceptions into completed aggregates. No cross-call deduplication or exactly-once delivery guarantee.

## Index outcome

If index requested, generate entries only from items whose execution final_job is COMPLETED, using source stem and output filename in deterministic item order. Reuse HtmlRenderer.render_index and PublishingService.write_bytes directly without legacy publish logging. Preserve existing theme/language, URL encoding and escaping. Empty successful set produces the existing empty index behavior.

Revalidate index output policy and alias protections immediately before index rendering/writing; retain atomic no-overwrite race protection at commit. Expected I/O/validation/publication failures produce BatchIndexFailure separately and leave item outcomes intact. No index job is introduced in this sprint. No raw exception messages are included in public aggregate diagnostics or logs.

## Commit and failure semantics

Each document and index commit is independent. A failed item may leave a committed file when its cleanup fails; it remains FAILED and is excluded from index. Index failure never removes committed document outputs. No automatic rollback, deletion or restore of committed destinations.

Reuse the existing atomic writer cleanup; distinguish precommit preservation from failures after successful commit. Log stable codes, stage names and job IDs only, excluding document content, source paths and raw cause messages in the new path.

## Compatibility and verification

Legacy batch result/API and CLI output/exit codes remain unchanged because their routing is not migrated. Single HTML CLI, DOCX/PDF and default runtime coordinator remain compatible.

Tests live in tests/batch_pipeline. Add independent >=95% bgdxpublisher.batch_pipeline coverage alongside total >=99% and existing five >=95% package gates. Installed-wheel tests outside checkout must cover full success, partial failure and an independent index failure on all four Windows/Linux Python 3.13/3.14 jobs.
