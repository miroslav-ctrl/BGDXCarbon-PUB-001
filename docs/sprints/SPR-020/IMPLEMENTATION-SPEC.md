# SPR-020 Implementation Specification

Status: proposed; no implementation.

## Public API and runtime

New bgdxpublisher.docx_batch_pipeline exports BatchDocxRequest,
BatchDocxItem, BatchDocxPublicationResult, BatchDocxPublicationError and
BatchDocxPublicationService. Follow existing batch HTML composition conventions.
Frozen/slotted BatchDocxRequest(source_dir: Path, output_dir: Path,
overwrite: bool=False, language: str="und"). No index/title/theme/TOC fields.
Service publish(request) -> BatchDocxPublicationResult.

BatchDocxItem(source: Path, output: Path, execution: JobExecutionResult) is
frozen/slotted. Require terminal consistent execution; completed pipeline output
must be PublishResult with matching output, failure must have output=None and
structured failure. Result freezes items into a tuple; reject empty item list,
duplicate source/output mappings and nonterminal/mismatched outcomes. Success
and failure counts are derived from terminal item status, not mutable counters.
Mixed/all-failed completed attempts return a result, not a batch exception.

BatchDocxPublicationError derives from PublisherDomainError with fixed
BATCH_DOCX_PREFLIGHT_FAILED string/code, raised from internal expected preflight
cause. It signifies no child publication attempted (directory setup may have
partially created directories). Per-item failures retain existing structured
DOCX_PUBLICATION_FAILED execution/code/stage; no synthetic parent batch job or
new engine semantics. Result paths are explicit caller-requested API data, not
safe log messages. Do not promise raw paths absent from explicit result fields.

Runtime registers new service alongside unchanged DocxPublicationService and
legacy DocxPublishingService, reusing registered single service through constructor
injection. Each item uses its own fresh document/job/context through publish.
Generic runtime/engine services and all commands/direct APIs remain unchanged.
Caller owns initialize/start/try-finally-stop; batch service never stops runtime.

## Preflight and selection

Validate language with existing validator before publication/directory creation.
Resolve source directory; missing/non-directory source is preflight failure.
Reject symbolic-link source root and any immediate .md candidate that is a symlink
(including dangling links); do not silently follow them. This is explicit new API
policy; existing HTML batch and single-document policies remain unchanged.
Select only immediate regular .md files case-insensitively; ignore subdirectories
and other extensions. Freeze one source snapshot sorted by (name.casefold(),name).
Empty selection fails preflight. Reject casefold duplicate target stems before
publication, on every platform. index.md is allowed: this API creates no index.

Map each source stem to <stem>.docx and title=None (single API resolves stem).
Validate output_dir is not a symlink or existing non-directory. Before any
publication or mkdir, reject planned output aliases/symlinks to any selected
input (samefile/hardlink) and output destination directories. Ordinary existing
regular output with overwrite=False is an item validate failure, not batch
preflight abort; later eligible items still run. Preserve single API checks for
metadata/title/filesystem. Output in same directory as input is allowed if guards
pass; document commits cannot replace selected sources.

After read-only checks, mkdir output_dir(parents=True,exist_ok=True); expected
OSError/validation failure is safe preflight exception before child calls. No
directory rollback if setup partially succeeds. Only after setup succeeds invoke
children sequentially from frozen snapshot; no rescanning or recursive discovery.
No whole-batch transaction or guarantee against arbitrary concurrent filesystem
changes. Child API rechecks its validation/atomic writer policy at use time.

## Per-item execution, failure and cleanup

For each source call registered DocxPublicationService.publish exactly once with
DocxRequest(source, mapped output, overwrite, None, language); no legacy fallback
or duplicate read/render/write. On success retain execution; on DocxPublicationError
retain error.result as FAILED item and continue. Catch only that typed child
failure for continuation. Unexpected service/runtime/programming exception outside
existing engine wrappers propagates immediately, stops later attempts and leaves
earlier outputs; do not invent an aggregate success or convert it to preflight.

Full successful run returns all COMPLETED items; partial/all expected failures
return matching ordered terminal items with accurate derived counts. No CLI exit/
stdout contract in this API-only sprint. Each output atomic independently; refused
output bytes/source preserved. Precommit errors clean temporaries/preserve previous
files. Postcommit registered cleanup failure is FAILED/stage=cleanup, no successful
output envelope, but file remains; count as failed and continue. Internal writer
cleanup failures remain write stage. Existing context cleanup order/once policy
and fresh job IDs per item/repeated invocation remain. No delete/restore/rollback.

New logs/error strings use fixed codes, stages, IDs or counts, never source/output
paths, filenames, titles, Markdown, DOCX bytes or raw cause. Internal cause of
preflight error stays inspectable; item execution keeps safe failure metadata as
existing batch HTML does, without promising a stored per-item raw exception object.
Legacy/new single-document diagnostics remain unchanged.

## Fidelity, installed distribution and quality

Compare every batch-generated document against individual DocxPublicationService
under identical dependencies: OOXML member inventory and all uncompressed member
contents, metadata/title/lang/styles/text/list/link semantics and source bytes.
Ignore ZIP timestamps/compression only; any observed volatile XML field needs
narrow written justification. Do not require whole-ZIP byte equality. Cover
Unicode/BOM, empty Markdown, different documents and stable order.

New tests/docx_batch_pipeline/test_docx_batch_publication.py (unique basename) and
examples/docx_batch_pipeline.py. Fresh installed-wheel example outside checkout,
source PYTHONPATH removed: installed imports, success, mixed/all failure,
refusal/overwrite, safe preflight and per-item metadata/status/counts. Retain
actual existing CLI/API smoke. Generate distinct batch DOCX preview artifact
through new API with >=2 differently formatted documents; render and inspect all
pages. Existing single DOCX preview alone cannot prove batch selection/outcomes.

Add independent >=95% bgdxpublisher.docx_batch_pipeline gate (nine total), preserve
existing eight and total >=99%, Ubuntu/Windows Python 3.13/3.14, Ruff/Black/MyPy.
No runtime/development dependency or version bump. Existing HTML/DOCX/PDF/batch
HTML behavior remains covered; new batch DOCX CLI is future work.
