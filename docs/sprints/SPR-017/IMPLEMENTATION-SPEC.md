# SPR-017 Implementation Specification

Status: implemented for review; approved contracts retained below. See IMPLEMENTATION-EVIDENCE.md.

## Dispatch and success

Keep run_publish signature and argparse declarations/defaults unchanged:
publish-docx source --output, --overwrite, --config, --title and --lang.
No theme/TOC/new options for DOCX. Preserve PDF-first, DOCX-second, HTML-otherwise
precedence, including direct run_publish calls with both flags true.
Only DOCX branch resolves DocxPublicationService once and calls publish with
DocxRequest(source, output, overwrite, title, language). Adapt result.publication
into the existing PublishResult-shaped success path. No legacy fallback or
duplicate publication. Successful stdout is exactly Published: <output path>
plus newline, emitted only after successful runtime shutdown, exit 0.

## Expected DOCX failures and stderr

Catch DocxPublicationError explicitly (PublisherDomainError, not assumed to derive
from RuntimeFoundationError). For an expected failed DOCX execution emit exactly
one primary CLI diagnostic line:
Publication failed: DOCX_PUBLICATION_FAILED stage=<stage>
plus newline; exit 1, no Published stdout.

Read stage from structured error.result.pipeline_result.failure. Internal stage
names are validate, read, render, write and cleanup. Never stringify/traverse the
cause to construct output. No raw input/output path from exceptions, title,
Markdown, rendered bytes or traceback in this new publication diagnostic.
Success stdout may retain requested output path. Existing safe code/stage/job-ID
logs may additionally appear on stderr; distinguish logs from primary CLI lines.

Argparse rejects missing required arguments or invalid title/lang/unsupported
options with exit 2 before runtime construction. A syntactically valid missing
source, invalid extension or filesystem/operational problem is pipeline exit 1.
This intentionally changes legacy DOCX operational error text, not exit codes;
document that compatibility boundary in USER-GUIDE and CHANGELOG. Existing
runtime/configuration diagnostics retain their current format and are outside
the new publication-message guarantee.

## Runtime lifecycle and precedence

Initialize/start once; stop CONFIGURED/RUNNING application in finally on success
and expected failure, not CREATED/FAILED initialization states. Keep current
runtime failure prefixes and existing HTML/PDF/batch behavior. Primary DOCX
publication failure remains the primary diagnostic when stop also raises an
expected RuntimeFoundationError; keep Runtime cleanup failed: <runtime error>
as the separate cleanup diagnostic. Preserve existing adapter diagnostic ordering:
cleanup diagnostic is emitted during finally, then the primary Publication failed
line. Never add a second publication failure for the shutdown cause when a
primary DOCX failure already exists.

Shutdown failure after completed DOCX returns 1 and suppresses Published stdout.
Use the existing runtime-error publication diagnostic in that case; committed
file remains. Pipeline cleanup failure returns safe stage=cleanup even if output
was committed. No deletion, restoration or rollback promise.

Unexpected programming exceptions are not converted to success or fabricated
DocxPublicationError. Preserve an active unexpected DOCX primary exception if
DOCX shutdown also fails unexpectedly; use only a safe secondary note, not user
content/raw causes. With no active primary, unexpected shutdown exception
propagates. Scope any necessary precedence handling to DOCX so unrelated command
semantics are not inadvertently changed. Existing engine policy governs stage
exceptions; this is not a new engine exception policy.

## Compatibility and test boundaries

Leave legacy DocxPublishingService.publish, DocxRequest, PublishResult,
PublishingError/cause behavior, renderer and new DocxPublicationService API
unchanged. Legacy direct callers retain existing raw diagnostics/logging.
Keep HTML, PDF and batch routes/tests unchanged. Update only DOCX CLI selection
assertions from SPR-016: its CLI-legacy spy becomes a direct-API compatibility
regression plus a CLI-new-route spy; keep original SPR-016 evidence historical.
Do not delete useful coverage simply because CLI routing changed.

Compare CLI-produced DOCX with legacy service outputs using member sets and
uncompressed OOXML members/semantic structures under identical dependencies.
Ignore ZIP timestamps/compression only; any XML normalization must be narrowly
justified. Preserve metadata, styles/language, Unicode/BOM, lists, links and safety.
No brittle independently-created ZIP byte equality promise.
