# SPR-019 Implementation Specification

Status: implemented for review; approved contracts retained below. See IMPLEMENTATION-EVIDENCE.md.

## Dispatch and success

Keep cli/app.py argparse declarations/defaults and run_publish signature unchanged.
Existing publish-pdf takes source, --output (required), --overwrite, --config,
--title and --lang (und). No theme/TOC/new options. PDF-first, DOCX-second,
HTML-otherwise precedence remains, including direct calls with both flags true.
PDF branch resolves registered PdfPublicationService once and calls publish with
PdfRequest(source, output, overwrite, title, language), then adapts
result.publication into existing success path. No legacy fallback/duplicate call.
On successful publication AND stop: exactly `Published: <output path>` plus newline,
exit 0. Result output/bytes_written and document content retain existing contract.

## Errors and compatibility

Catch PdfPublicationError explicitly (PublisherDomainError, not assumed to derive
from RuntimeFoundationError). Expected failed PDF execution yields exactly one
primary CLI line `Publication failed: PDF_PUBLICATION_FAILED stage=<stage>` plus
newline; exit 1, no Published stdout. Get stage from structured
error.result.pipeline_result.failure; validate/read/render/write/cleanup.
Never stringify/traverse raw cause to construct diagnostic. No raw paths, title,
Markdown, PDF bytes, unsupported user characters/glyph code or traceback in this
new publication diagnostic. Safe code/stage/job-ID logs may accompany the primary.

Argparse rejects missing required args, invalid title/lang and unsupported options
with precise existing diagnostics/exit 2 before runtime construction. Valid syntax
with missing source, invalid .pdf extension or invalid output path is operational
exit 1/stage=validate; invalid UTF-8 is read. Unsupported glyph/control, font
TTFError or LayoutError is safe render failure; writer failure is write.
Engine-owned registered cleanup failure after commit is cleanup. Internal writer
cleanup exceptions remain write under unchanged engine policy.

This intentionally replaces legacy CLI operational cause/glyph-code messages.
Document boundary in USER-GUIDE/CHANGELOG and affected current README/examples.
Legacy PdfPublishingService direct API still exposes its original errors/cause/
logging (including unsupported glyph detail). Pipeline API stays unchanged.
Runtime/configuration failures retain current formats and are outside the new
safe publication diagnostic guarantee. Do not silently broaden that guarantee.

## Runtime lifecycle and precedence

Initialize/start once; finally stop CONFIGURED/RUNNING applications on success or
failure, not CREATED/FAILED initialization states. Preserve DOCX/HTML/batch/default
runtime behavior and generic runtime semantics. Scoped PDF handling must also
apply with both flags true, while existing DOCX protection remains intact.

Expected RuntimeFoundationError during stop:
- After expected PDF publication failure: existing `Runtime cleanup failed:
  <runtime error>` line first, then original safe PDF primary line, exit 1;
  exactly one primary publication line, no Published stdout.
- After successful PDF: cleanup line then existing runtime-error `Publication
  failed: <runtime error>` line, exit 1/no Published; committed file retained.
- During active unexpected PDF exception: do not mask it with shutdown error;
  retain existing expected-runtime diagnostic behavior and propagate primary.

Unexpected non-runtime Exception during stop:
- Active unexpected PDF primary: propagate original primary with only a fixed,
  safe secondary note (no raw stop cause/content); no fabricated PdfPublicationError.
- No active unexpected primary (including success or an already handled typed
  PDF failure): propagate unexpected stop exception; do not convert it to safe
  operational exit 1 or success. This matches existing DOCX adapter policy.

Unexpected exceptions outside stage execution keep normal propagation. Existing
engine stage exception policy remains unchanged. Pipeline cleanup failure returns
safe stage=cleanup/no success even after commit. Runtime stop failure and pipeline
cleanup are distinct; no deletion/restoration/rollback promise for committed PDF.
Test exact diagnostic order/count and exception precedence, not only substrings.

## Fidelity and test boundaries

Leave PdfPublishingService.publish, PdfRequest, PublishResult, PublishingError,
PdfPublicationService, renderer/fonts/writer/engine/registration/dependencies
unchanged. Preserve new/legacy direct APIs and all unrelated command tests.
Replace only obsolete PDF CLI-legacy-selection assertions with CLI-new-route spies
and direct legacy compatibility regressions. Update PDF-first test currently in
tests/cli/test_docx_runtime_precedence.py to spy new PDF service while still
forbidding DOCX; preserve its precedence coverage. Keep SPR-018 evidence historical.

Compare CLI output with legacy and/or already verified pipeline API under identical
dependencies. Cover UTF-8/BOM, empty/complex/multipage Markdown, default/custom
metadata, Latin/Cyrillic, safety/fonts, page count/order/A4/text/content streams,
title/catalog language and URI rects/targets. Ignore only observed justified
volatile PDF IDs/timestamps/serialization; do not broadly discard content/metadata
or require independently generated whole-file byte equality.

Retain filesystem overwrite/refusal/alias/symlink/race/permission/precommit tests
and postcommit cleanup once/context isolation. Run actual installed publish-pdf
outside checkout with source PYTHONPATH removed: success/refusal/overwrite,
parser rejection, safe validate/read/render failures. Retain installed API smoke.
Existing CLI-generated pdf-preview now proves migrated route; actually inspect
its pages on tested SHA. Retain separate API multipage/DOCX preview checks.
