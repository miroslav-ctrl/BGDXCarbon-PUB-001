# SPR-022 Implementation Specification

Status: implemented for Draft review; approved contract retained below.
See [implementation evidence](IMPLEMENTATION-EVIDENCE.md).

## Public models and runtime composition

New bgdxpublisher.pdf_batch_pipeline exports BatchPdfRequest, BatchPdfItem,
BatchPdfPublicationResult, BatchPdfPublicationError, BatchPdfPublicationService.
Follow established DOCX batch composition without modifying that package.
Frozen/slotted BatchPdfRequest(source_dir:Path,output_dir:Path,
overwrite:bool=False,language:str="und"). No title/index/theme/TOC/CLI fields.
Service publish(request)->BatchPdfPublicationResult.

BatchPdfItem(source:Path,output:Path,execution:JobExecutionResult) is frozen/slotted.
Accept only consistent terminal executions: COMPLETED requires matching
PublishResult output path; FAILED requires output=None/structured failure, with
existing job/pipeline/status-history invariants. Result freezes items to tuple;
reject empty list, duplicate source or output mappings, nonterminal or mismatched
outcomes. Derive success_count/failure_count from terminal job status. Mixed/all
expected child failures return ordered terminal result, not a batch exception.
Result paths are explicit API data and intentionally visible to the caller.

BatchPdfPublicationError derives PublisherDomainError, fixed string/code
BATCH_PDF_PREFLIGHT_FAILED, raised from internal expected validation/OSError cause;
it means no child attempted, though mkdir may partially create directories.
No synthetic parent batch job or new engine status. Per-item typed child failures
retain error.result with existing safe pipeline failure code/stage/type metadata;
no promise of storing raw exception objects on every item. PDF_PUBLICATION_FAILED
is the existing typed single-publication wrapper code, not a newly invented
PipelineFailure.error_code value.

Constructor takes logger and optional PdfPublicationService dependency as existing
DOCX batch service does. Runtime registers new service alongside unchanged single
PDF/legacy PDF services, injecting the exact already registered PdfPublicationService.
Each child publish creates fresh document/job/context. Caller owns initialize/
start/try-finally-stop; batch service neither starts nor stops runtime. Existing
CLI shutdown/primary-error behavior and generic lifecycle are untouched.

## Read-only preflight and frozen selection

Validate language with existing validator before directory creation or children.
Check source root is not a symlink BEFORE resolve; missing/non-directory rejects.
Enumerate immediate .md candidates case-insensitively once. Reject candidate
symlinks including dangling links before filtering regular files; ignore other
extensions/subdirectories, select regular files only. Freeze tuple sorted by
(name.casefold(),name); reject empty selection and duplicate casefold stems on
all platforms. index.md allowed; this API generates no index. Map stem to .pdf,
pass title=None so single service uses source stem. No rescan between children.

Output root: reject symlink/existing non-directory. Before mkdir/any child, check
EVERY planned output: reject every symbolic link including dangling/unrelated
outputs in both overwrite modes, destination directory, aliases to ANY selected
input by same path/samefile/hardlink. Protect all inputs before first child, not
just each current source. Same source/output directory allowed when guards pass.
Existing ordinary regular output with overwriteFalse remains individual validate
failure, so later eligible documents run. Single API retains metadata/title/
filesystem/atomic rechecks at time of use; no changes to prior policies.

Only after ALL read-only guards: mkdir(parents=True,exist_ok=True). Expected
OSError/validation failure -> safe preflight exception/no children. No directory
rollback if setup partly succeeds. No arbitrary concurrent filesystem isolation,
recursive discovery or whole-batch transaction guarantee.

## Sequential outcomes, failures and cleanup

Invoke registered single PdfPublicationService.publish EXACTLY ONCE per source,
sequentially, exact PdfRequest(source,mapped_output,overwrite,None,language).
No fallback to legacy publish, duplicate read/render/write or CLI invocation.
Success retains completed execution; catch ONLY PdfPublicationError for expected
per-item continuation, retaining error.result. Unexpected external child/runtime/
programming error outside engine wrappers propagates immediately/stops later
attempts, earlier committed PDFs remain. Do not relabel it preflight or fabricate
aggregate success. Engine's existing exception policy remains unchanged.

Invalid UTF-8 -> read failure; invalid filename-derived title -> validate;
unsupported glyph/control, font/TTFError/LayoutError -> render; atomic/write/temp
failures -> write. Preserve existing PDF single API behavior, including licensed
embedded fonts, Latin/Cyrillic, empty Markdown and automatic pagination. Unsupported
glyph remains typed failed item; eligible later sources run. No renderer/font or
semantic capability extensions and no raw glyph details in new safe batch logs.

Full completed attempts return accurate success/failure counts including all
expected failures. Registered engine cleanup AFTER commit -> FAILED/stage=cleanup,
output=None, file retained/count failed/continue. Internal writer cleanup error
stays write stage; no rollback/delete/restore. Context cleanup order/once/fresh IDs
across items and repeated invocations inherited unchanged. Source/previous bytes
survive refusal/precommit failure and each output commits independently.

New error strings/logs use fixed codes/stages/IDs/counts, no path/name/title/text/
PDF bytes/raw cause. Preflight internal cause is inspectable; explicit result
paths intentionally visible. Existing single pipeline/legacy diagnostic contracts
remain unchanged, and unexpected external errors retain propagation. No new CLI
exit/stdout/stderr contract in this API-only sprint.

## PDF fidelity and installed acceptance

Compare each batch PDF with individual PdfPublicationService for identical source,
options and dependencies. Host pypdf semantic assertions: page count/order/A4
boxes, extracted Unicode/text and layout content, decoded page content streams,
font/resource/encoding/embedded-font semantics, title/catalog language and URI
annotation destinations/rectangles. Source bytes unchanged. Do not compare whole
independently generated PDF bytes; exclude ONLY observed volatile document IDs/
creation-modification timestamps or serialization differences with narrow written
justification. Do not discard metadata/content/resources wholesale. No runtime
pypdf dependency: keep it existing dev/CI-host parser only.

New tests/pdf_batch_pipeline/test_pdf_batch_publication.py (unique basename),
examples/pdf_batch_pipeline.py using runtime dependencies only. Fresh installed
wheel outside checkout, source PYTHONPATH removed, copied example -I, installed
import assertion. Verify success/refusal/overwrite/mixed/all failure/safe preflight,
ordered statuses/stages/counts and metadata as appropriate. Keep final success
samples for HOST pypdf assertions; installed venv is not required to import pypdf.
Include unsupported glyph + later successful child and invalid UTF-8 cases.
Retain every existing installed CLI/API smoke; no new batch PDF command.

Distinct pdf-batch-preview generated through NEW API with >=2 differently
formatted sources, including one single-page and one multipage output. Rasterize
ALL PDF pages on CI and actually inspect every page; record source/merge SHA,
run/job/artifact/digest and exact page scope. Keep existing single PDF/API and
DOCX/API/CLI previews; existing previews alone do not prove new batch execution.

Add tenth independent>=95% bgdxpublisher.pdf_batch_pipeline gate; retain all
nine existing gates and total>=99%, Ubuntu/Windows Python3.13/3.14/Ruff/Black/MyPy.
No dependency/version bump. Align README/USER-GUIDE/examples/CHANGELOG/release guide
with development API and ten gates while preserving published1.1.0 notes/history.
Accepted1.2.0 scope remains future/unpublished; batch PDF CLI remains SPR-023.
