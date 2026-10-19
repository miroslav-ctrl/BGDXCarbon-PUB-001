# SPR-016 Implementation Specification

Status: proposed, not implemented.

## Public contracts and composition

New package bgdxpublisher.docx_pipeline exports DocxPublicationService,
DocxPublicationResult and DocxPublicationError.
Proposed publish(request: DocxRequest) -> DocxPublicationResult.
Result is frozen/slotted: publication: PublishResult, execution: JobExecutionResult.
Reject non-COMPLETED execution and mismatched pipeline output/publication.
DocxPublicationError derives from PublisherDomainError, stable code
DOCX_PUBLICATION_FAILED, retains only a consistent FAILED execution in result and
raises from JobExecutionError. A failed pipeline exposes no partial success output.

Use JobService, PipelineEngine and JobExecutionService following html_pipeline.
Each call creates independent document/job IDs and an engine-owned context;
MARKDOWN document identity uses fixed safe metadata (e.g. DOCX publication /
docx-pipeline), not user paths/title/body. Preserve status history and safe logs.
Runtime registers new service alongside DocxPublishingService. No CLI dispatch
or legacy direct-API change in SPR-016.

## Stages

Each stage has explicit name/input_type/output_type; immutable typed snapshots:

1. validate: DocxRequest -> ValidatedDocxRequest. Resolve existing source; require
   regular file; reject same path and hard-link alias; require .docx suffix
   case-insensitively; apply shared validate_output and existing-parent policy.
   Resolve title from source stem if None; validate title/language before reading.
2. read: validated options -> DocxSource(options, text). Read once as utf-8-sig
   to support UTF-8 with/without BOM; never modify source.
3. render: source -> RenderedDocx(options, content: bytes). Call existing
   DocxRenderer.render once with validated text/title/language. Do not invoke
   DocxPublishingService.publish as fallback.
4. write: rendered bytes -> PublishResult. Call PublishingService.write_bytes
   once with overwrite policy; bytes_written matches actual serialized content.

Pipeline order: validate, read, render, write. Shared validators/writer may be
used without copying renderer logic or changing legacy exception text. Expected
validation/read/render/write failures become structured stage failures with
preserved internal cause chain; do not log/stringify raw causes or content in
the new service. Existing engine semantics govern unexpected stage exceptions;
do not introduce a broad service-level fallback or reinterpret engine policy.

## Filesystem, cleanup and logging

Retain overwrite refusal/replacement, source/alias/output-symlink guards, atomic
no-overwrite race protection, temporary cleanup and permissions policy.
Validate makes no document content writes or parent creation. Precommit failure
preserves existing output/source. After atomic commit, cleanup failure yields
FAILED / stage=cleanup, no successful result, but the committed DOCX remains.
No deletion, restoration or rollback promise. Repeat calls use distinct contexts;
cleanup runs exactly once according to existing engine contract.

Logs in the new route contain fixed codes, stages and IDs only, excluding source/
output paths, Markdown, title, rendered bytes and raw cause messages.
Legacy DocxPublishingService logging/diagnostics remain unchanged and are outside
the new safe-log contract.

## DOCX compatibility comparison

Reuse DocxRenderer unchanged. Compare OOXML package member sets and uncompressed
member contents/parsed XML or equivalent semantic structures for identical inputs
and dependency versions. Compare metadata, styles/language, paragraph/run text and
formatting, headings, list numbering/nesting, quotes/code, link relationships and
absence of embedded images/macros. Ignore ZIP container timestamps/compression
differences only; do not broadly discard relationship IDs, content, metadata or
ordering to hide differences. If a volatile XML field is observed, document and
narrowly justify its normalization before accepting the comparison.
Do not promise byte-for-byte equality of independently generated .docx ZIP files.

## Verification and CI

Tests proposed at tests/docx_pipeline/test_docx_publication.py (unique basename).
Add independent >=95% coverage for bgdxpublisher.docx_pipeline alongside total
>=99% and all six existing >=95% gates. Keep Ubuntu/Windows Python 3.13/3.14.
Fresh-wheel API example must run outside checkout with installed imports and
validate OOXML success, refusal/overwrite, expected failure and retained outputs.
Existing real publish-docx CLI/wheel and DOCX visual sample steps remain intact.
