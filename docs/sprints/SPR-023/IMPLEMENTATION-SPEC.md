# SPR-023 Implementation Specification

Status: proposed plan; owner authorized planning, implementation and merge in this task.
Plan and implementation CI/reviews are separate execution gates.

## AC-01: command and dispatch

New command: `bgdxpublisher publish-pdf-batch SOURCE --output-dir DIR
[--overwrite] [--config PATH] [--lang TAG]` (one logical command line).
SOURCE and DIR are pathlib.Path; output-dir required; overwriteFalse/configNone/
languageund defaults. Use existing _metadata_argument(validate_language).
No --output/--title/--theme/--toc/--index/recursive option or alias; unsupported
arguments and invalid language/missing required args produce argparse exit2
before runtime construction. --help exits0 before runtime. Parser messages retain
argparse detail; they are outside safe operational diagnostic guarantees.

New cli/pdf_batch.py run_pdf_batch(source:Path, output:Path, overwrite:bool,
config:Path|None, language:str)->int. app.py imports and dispatches exact values;
no changes to existing run_batch/run_publish signatures or handlers. Construct
one PublisherApplication(config_path=config), initialize/start once, resolve
registered BatchPdfPublicationService once, call publish once with exact
BatchPdfRequest(source,output,overwrite,language). No legacy fallback or direct
per-file service calls by CLI. Existing batch service owns discovery/execution;
CLI never rescans sources, renders/writes, synthesizes jobs or stops per item.

## AC-02/03: terminal projection and success output

Use service-provided order. Each COMPLETED item contributes exactly
`Published: <item.output>` plus newline to buffered stdout. Paths are intentional
success data; no filename-based stderr. Derive counts from result.success_count/
failure_count, consistent with terminal statuses. Buffer summary after item lines:
`Batch complete: <success_count> published, <failure_count> failed.` plus newline.
No index/extra success report. After successful runtime stop, emit buffered stdout
once: all success exit0; mixed/all expected failures exit1 with same summary
(including `Batch complete: 0 published, N failed.`). Never claim FAILED cleanup
item Published even if committed file exists. No whole-batch transaction.

## AC-04/05: expected diagnostics and API compatibility

For each FAILED item immediately emit exactly one stderr line in result order:
`Failed: item=<1-based ordinal> PDF_PUBLICATION_FAILED stage=<stage>` + newline.
Ordinal counts ALL result items, including completed ones; take stage from
item.execution.pipeline_result.failure.stage_name (validate/read/render/write/
cleanup), never parse/stringify raw causes. Use fixed PDF_PUBLICATION_FAILED code.
Safe stage/code/job-ID logs may accompany these lines; do not print job IDs or
exception_type as additional CLI reports.

Catch BatchPdfPublicationError explicitly: one primary line
`Batch publication failed: BATCH_PDF_PREFLIGHT_FAILED` + newline, exit1, no
Published/summary stdout. No synthetic failed item/count if preflight never ran
children. Do not catch it as RuntimeFoundationError. Fixed diagnostic omits raw
source/output/name/title/body/bytes/cause/traceback. Internal cause and explicit
API result paths remain intentionally inspectable via direct API.

Preserve SPR-022 preflight/snapshot/symlink/alias/collision/index.md policies,
ordinary output refusal as per-item validate failure, typed failure continuation,
fresh execution and independent atomic outputs. Existing direct batch/single/
legacy APIs, exceptions, results, logging and signatures remain untouched. PDF semantic fidelity against the direct batch API; source/refused bytes retained.
No change to supported PDF renderer semantics/fonts or common engine policy.

## AC-06: runtime shutdown, output timing and exception precedence

One runtime; finally stop once only when state CONFIGURED or RUNNING. CREATED/
FAILED initialization states are not stopped; failed start in CONFIGURED is
stopped. Keep new adapter separate from existing commands/generic runtime code.

Expected RuntimeFoundationError during initialize/start/resolve/publication:
`Batch publication failed: <runtime error>` + newline, exit1, no stdout.
If construction raises, preserve existing unhandled constructor behavior;
constructor failures are outside this adapter's expected-runtime catch.
Runtime/config error messages retain established formats; this contract does not
claim their raw details are sanitized. Safe fixed publication diagnostics above
must not be replaced by raw child causes.

Buffer ALL Published/summary stdout until body and shutdown complete; safe
per-item/preflight/runtime stderr diagnostics are emitted when handled in body.
On expected RuntimeFoundationError during stop: emit exactly one
`Runtime cleanup failed: <runtime error>` + newline; suppress ALL buffered stdout,
return1 if no unexpected primary is propagating. Preserve already emitted item/
preflight diagnostics; no duplicate Batch publication failed primary. After body
success, cleanup line alone explains exit1; no fabricated publication failure.
Committed outputs remain, even though CLI reports no successful completion.

Unexpected Exception outside existing engine wrappers during body: do not
convert to safe preflight/result or invent counts. Propagate after finally;
CLI stdout stays empty (service may have committed earlier files). If stop then
raises expected RuntimeFoundationError, emit established cleanup line and retain
original unexpected primary. If stop raises unexpected non-runtime Exception:
- Active unexpected primary: re-raise original with ONE fixed safe note
  `An unexpected runtime cleanup failure occurred.`; never stringify the stop
  cause in that note.
- No active unexpected primary (body success, handled typed preflight/item result
  or handled runtime failure): propagate unexpected stop itself; no exit1
  conversion and no buffered stdout. Use actual active exception, not a handled
  error/result flag, to choose precedence. Do not call stop again.

Engine-owned registered cleanup and runtime.stop are distinct. Postcommit child
cleanup means FAILED/stage=cleanup/output=None/file retained/continue, then usual
failed item diagnostic/summary if runtime stop succeeds. Writer cleanup failure
remains write stage. Runtime-stop failure suppresses reports, not committed files.
No deletion/restoration/rollback. Explicitly test the precedence/stream matrix:
body success/mixed/all/preflight/expected-runtime/unexpected, each paired with
successful stop/expected stop/unexpected stop, plus startup-state boundaries.

## AC-07/08/09: verification, packaging and documentation

New tests/cli/test_pdf_batch_cli_pipeline.py and
 tests/cli/test_pdf_batch_runtime_precedence.py (unique basenames), copied
examples/pdf_batch_cli_pipeline.py for fresh installed-wheel verification.
Keep existing examples/pdf_batch_pipeline.py and all existing API/CLI smoke.
Real installed executable outside checkout with source PYTHONPATH removed:
help/arguments/defaults/config routing/success/refusal/overwrite/mixed/all failure/
safe preflight/item stage diagnostics. Injection against installed adapter is
allowed for deterministic runtime failures, with no production testing hooks.
Use the existing host/dev-only examples/pdf_batch_verify.py comparison for CLI-vs-direct
batch outputs on identical inputs/dependencies: page order/count/A4/text/decoded
streams/resources/embedded fonts/metadata/lang/URI. Only observed CreationDate/
ModDate and trailer ID volatility plus stream transport normalization are excluded,
under the established SPR-022 contract. Runtime-only example must not import pypdf.
Keep actual installed existing CLI/API tests and semantic checks.
Distinct CLI-generated pdf-batch-cli-preview via actual publish-pdf-batch with
>=2 different documents (Latin/Cyrillic/formatting), including a multipage PDF; render all output pages and
actually inspect every page. Retain existing batch API and single PDF/PDF previews.
No assumption that mere artifact upload establishes manual visual acceptance.

CI remains Ubuntu/Windows Python3.13/3.14, total>=99%, all ten existing package
gates>=95%; no new package gate needed for a CLI adapter. Full/static tests required,
not baseline tests alone. No version/dependency changes. Update README/USER-GUIDE/
examples/CHANGELOG current descriptions and release guide's current ten-gate
statement; preserve published1.1.0 release notes/history. Document new batch CLI,
API availability, safe errors/partial results/overwrite/runtime shutdown limits.
Keep1.2.0 as accepted future edition; no claim it is already shipped.
