# SPR-021 Acceptance and Closure Evidence

Verified 2026-10-21 on merged develop
`285d6ac5de8deb55105d96ed96f7dec3574b52d5`. Technical implementation acceptance
passes; closure documentation submitted for review. Administrative closure remains
pending and issue #59 stays open.

## Provenance

- Approved plan [PR #58](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/58), implementation baseline `c65c64c337c0ca9d2ad147e17456b2ef3e3852e4`.
- Implementation [PR #60](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/60), reviewed head `04c34ac56564b9cdf20ebce6e74eb67e89e96049`.
- [Formal implementation review](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/60#pullrequestreview-5597508046): no blocking findings. Disclosed Codex COMMENT, not independent human APPROVE.
- Owner accepted the review, authorized Ready for review, then separately authorized merge into develop in this task.
- Implementation merge: `285d6ac5de8deb55105d96ed96f7dec3574b52d5`.
- [Exact post-merge Publisher CI 39576893636](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39576893636): push to develop at that merge SHA, completed/success.

## Executed exact-merge checks

| Environment | Job | Full suite | Total coverage | DOCX batch gate | HTML batch gate |
| --- | --- | --- | --- | --- | --- |
| Ubuntu / Python 3.13 | [119144516461](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39576893636/job/119144516461) | 652 passed | 99.91% | 100% | 100% |
| Ubuntu / Python 3.14 | [119144516600](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39576893636/job/119144516600) | 652 passed | 99.91% | 100% | 100% |
| Windows / Python 3.13 | [119144516730](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39576893636/job/119144516730) | 649 passed, 3 skipped | 99.91% | 100% | 99.04% |
| Windows / Python 3.14 | [119144516888](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39576893636/job/119144516888) | 649 passed, 3 skipped | 99.91% | 100% | 98.99% |

All four jobs succeed. Windows skips three case-sensitive collision cases (HTML
batch API, DOCX batch API and new DOCX batch CLI); Linux executes all cases.
Hosted symlink cases execute. Nine independent >=95% package gates retained:
domain, jobs, pipeline, orchestration, html_pipeline, batch_pipeline,
docx_pipeline, pdf_pipeline, docx_batch_pipeline. All except HTML batch as
tabulated are 100%; full suite total >=99% retained.

Executed ci.yml commands: python -m ruff check ., black --check ., mypy src,
pytest full suite, full coverage --cov-fail-under=99, nine independent package
coverage commands --cov-fail-under=95, pip wheel . --no-deps --wheel-dir
dist-review, full fresh installed-wheel smoke and configured visual generation.
Historical local results remain distinct in [IMPLEMENTATION-EVIDENCE.md](IMPLEMENTATION-EVIDENCE.md):
Windows Python3.13.14 full617passed/35filesystem skips,total99.78%, new adapter
43statements100%;66new cases with51passed/15filesystem skips. Formal review
rerun186passed/31filesystem skips. No new local code tests/wheel build claimed
by this documentation submission; hosted checks verify exact merged integration.

Fresh temporary installed wheel runs outside checkout with PYTHONPATH removed
and new copied example -I/installed-import assertion. Actual publish-docx-batch
executable verifies config/lang/default publication, success/refusal/overwrite,
mixed/all/read/preflight/parser/help, safe diagnostics, metadata, source bytes and
all uncompressed OOXML member inventory/content vs direct batch API. No XML fields
excluded; ZIP metadata ignored. Installed adapter injection verifies expected
stop failure/retained files and active unexpected primary plus unexpected stop
fixed safe note, without production hooks. All existing installed CLI/API checks
and existing previews are retained/passing. Historical local wheel digest and
versions remain in implementation evidence and PR#60 verification comment.

## Actual exact-merge CLI visual inspection

Downloaded [docx-batch-cli-preview artifact 12334309696](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39576893636/artifacts/12334309696).
ZIP SHA256 checked against API artifact digest:
`0f5a119f116f914f6c45b13996662168fd8aeff6eba343b3bc2df70f1234da9b`.

examples/docx_batch_cli_pipeline.py invokes the actual installed command on two
distinct Markdown documents; published/notes.docx and report.docx are retained.
LibreOffice converts both to PDF; pdftoppm renders every page at100dpi. Actually
opened ALL pages: notes-page-1.png and report-page-1.png, one page per document.
Latin diacritics/Cyrillic, headings, quote, numbered/bulleted lists, bold/italic,
code and link are readable, with no visible clipping/overlap. Claim is limited to
these two samples, not every input/viewer. Existing batch API12335330176, single
DOCX12334756195, PDF12334970814 and PDF API12334642699 previews are retained and
checks pass; no new manual inspection of those artifacts is claimed here.

## Accepted behavior and compatibility limits

See [AC mapping](ACCEPTANCE.md). New cli/docx_batch.py and app.py new import/
subparser are the only production changes. New publish-docx-batch takes source,
required --output-dir, --overwrite, --config and --lang. Abbreviation disabled only
on new subparser, including --output rejection; existing parsers unchanged.
Initialize/start once, resolve registered batch service once, exact
BatchDocxRequest once; API alone owns discovery/fresh jobs and independent commits.
Direct batch/single/legacy APIs and existing CLI adapters, renderer/fonts/writer/
engine/runtime/registry/dependencies/version remain unchanged.

After successful stop, report Published per COMPLETED item and exact derived
Batch complete summary, exit0 only all completed; mixed/all failures exit1.
Per failed item: Failed: item=<1-based selection ordinal> DOCX_PUBLICATION_FAILED
stage=<stage>. Preflight: Batch publication failed: BATCH_DOCX_PREFLIGHT_FAILED,
exit1/no stdout or synthetic counts. Safe reports omit raw input/path/content/
cause/traceback; explicit success/API paths are intentional. Argparse/runtime/
config detailed formats stay outside safe expected-publication guarantee.
Parser errors exit2/help0 before runtime. Unexpected external errors propagate.

Finally stop once only CONFIGURED/RUNNING; no stop CREATED/FAILED initialization,
failed start CONFIGURED stopped. Buffer stdout until successful stop. Expected
stop error emits Runtime cleanup failed: <runtime error>, suppresses ALL buffered
stdout, preserves prior item/preflight reports and returns1 absent unexpected
primary. No duplicate or fabricated publication failure. Active unexpected body
primary survives expected stop error or unexpected stop error; the latter adds
one fixed safe note An unexpected runtime cleanup failure occurred. Without an
active primary (including handled error/result), unexpected stop propagates itself.
Full18-case body/stop matrix, startup/constructor and real partial-commit behavior
are tested. Engine registered cleanup is FAILED/stage=cleanup/output=None/file
retained/continue; writer cleanup stays write. No deletion/restore/rollback or
arbitrary concurrent filesystem isolation promise.

## Administrative disposition

Implementation review, owner acceptance, authorized implementation merge and
exact post-merge CI are complete. This record supersedes historical pending
review/merge/CI/visual dispositions in IMPLEMENTATION-EVIDENCE.md and planning
VERIFY.md without rewriting earlier executed results. Final closure-document
formal review/owner acceptance, separately authorized documentation merge and
exact documentation post-merge CI must precede completing
[issue #59](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/59).
This submission keeps issue open and performs none of those later actions.
SPR-021 contributes to accepted release1.2.0 scope; the edition is not published
or declared complete. No release/tag/version/dependency change/branch deletion;
main unchanged at `9883eca15ef4642db6513efa4fa3610158312f27`.
