# SPR-018 Implementation Specification

Status: implemented for review; approved contracts retained. See IMPLEMENTATION-EVIDENCE.md.

## Public API and runtime

New bgdxpublisher.pdf_pipeline exports PdfPublicationService,
PdfPublicationResult and PdfPublicationError. Service publish(request: PdfRequest)
returns frozen/slotted result(publication: PublishResult, execution:
JobExecutionResult); require COMPLETED and matching pipeline output/publication.
PdfPublicationError derives from PublisherDomainError, code PDF_PUBLICATION_FAILED,
requires consistent FAILED execution, exposes result and raises from
JobExecutionError. Failed execution has no successful/partial publication output.

Compose JobService, PipelineEngine and JobExecutionService like docx_pipeline.
Each invocation creates fresh document/job IDs and engine-owned context; fixed
safe MARKDOWN descriptor (PDF publication/pdf-pipeline), never paths/title/body.
Retain QUEUED/RUNNING/terminal history and immutable snapshots. Register alongside
PdfPublishingService; leave generic runtime services and existing registrations
intact. Preserve PdfRequest, PublishResult and all legacy public contracts.

## Typed stages

1. validate: PdfRequest -> immutable ValidatedPdfRequest. Resolve existing regular
   source; reject input/output same path/hardlink, output symlink/directory,
   invalid case-insensitive .pdf suffix, missing parent and overwrite refusal
   using shared guards. Resolve default title from source stem and validate
   title/language before reading. No parent creation or content writes.
2. read: validated options -> immutable PdfSource(options,text); one utf-8-sig
   read, unchanged source bytes (UTF-8 with/without BOM).
3. render: PdfSource -> immutable RenderedPdf(options,content:bytes); exactly one
   unchanged PdfRenderer.render(text,title,language). No legacy publish fallback.
4. write: RenderedPdf -> PublishResult through shared atomic write_bytes once;
   output and bytes_written reflect committed bytes.

Pipeline order validate/read/render/write; cleanup stage is owned by existing
engine. Use existing exception policy without new engine-wide catches. Invalid
metadata/path is validate; encoding/read is read; unsupported glyph/control,
LayoutError, TTFError/font or rendering error is render; commit error is write.
Preserve internal cause chain, job FAILED and structured stage; no invented
success or service-level fallback for programming errors.

## Safe diagnostics, filesystem and shutdown boundary

New API failure string is the fixed PDF_PUBLICATION_FAILED code; stage comes from
error.result.pipeline_result.failure.stage_name. Safe logs contain codes/stages/
IDs only; exclude input/output paths, titles, Markdown, PDF bytes, unsupported
user characters and raw exception messages. Internal causes remain inspectable.
Do not replace legacy PublishingError messages/logging or existing CLI diagnostics.
No new CLI error prefixes or exit behavior in this sprint.

Retain atomic refusal/overwrite, alias/symlink/race and permission protections.
Precommit failure preserves previous output and source, cleans temporaries.
Postcommit cleanup failure yields FAILED/stage=cleanup/no successful envelope,
but committed file remains; no rollback/delete/restore promise. Cleanup exactly
once in engine order; repeated calls have independent contexts.

New service does not own runtime startup/shutdown. API caller retains existing
initialize/start/try-finally-stop responsibility. Test registration and shutdown
on success/failure using existing runtime contract; no CLI finally/exception
precedence changes. publish-pdf still resolves legacy PdfPublishingService;
PDF-first dispatch when both PDF/DOCX flags are set remains unchanged. Direct
legacy callers retain result/errors/cause/logging, including glyph-code details.

## PDF compatibility evidence

Reuse PdfRenderer and bundled fonts unchanged. Under identical dependencies,
compare legacy and new API outputs with pypdf: page count/order, A4 media boxes,
extracted Unicode text per page, title and catalog language, safe URI annotations
and visible fallback labels, embedded font resources and valid PDF structure.
Cover headings/styles/lists/start/nesting/quotes/code/tabs, BOM, empty input,
custom/default metadata and multipage input. Retain renderer safety/glyph tests.
Do not promise raw independently generated PDF-byte equality: document IDs,
creation timestamps and serialization may vary. Do not broadly discard metadata,
text/order/links/fonts or geometry to hide differences. Any normalization must
name and narrowly justify an observed volatile field. Inspect actual rendered
new-API pages, including multipage pagination and long code, for layout regressions.

## Quality and distribution

New tests/pdf_pipeline/test_pdf_publication.py (unique basename), copied example
examples/pdf_pipeline.py outside checkout with source PYTHONPATH removed and a
fresh installed wheel. Verify installed imports, metadata/text, refusal/overwrite,
safe failures and retained output. Generate distinct PDF pipeline preview artifact
through the new API; retain existing CLI PDF/DOCX previews/checks.
Add independent >=95% bgdxpublisher.pdf_pipeline gate: eight package gates total,
existing seven untouched; total >=99%, Ubuntu/Windows Python 3.13/3.14,
Ruff/Black/MyPy. pypdf stays development-only; no runtime dependency/version bump.
