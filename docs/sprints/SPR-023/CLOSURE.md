# SPR-023 Acceptance and Closure Evidence

Verified 2026-10-22 on merged develop
`e74d343e3ebe4fd4aa9b44405a75ee74f74f798f`. Technical acceptance passes;
closure documentation submitted for review. Administrative closure remains
pending and [issue #67](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/67)
stays open. Release1.2.0 is not published or declared complete by this record.

## Provenance

- Plan [PR #66](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/66), merged `66c1a3b80f7650343633b05ef1425fcc61aded19`; [plan review](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/66#pullrequestreview-5610574337); exact plan post-merge CI39740035241 SUCCESS.
- Implementation [PR #68](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/68), reviewed head `29ef18e6376bc8fe5a1841b78e2fab3c9bafdeef`.
- [Formal implementation review](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/68#pullrequestreview-5610674097): no blocking findings. Codex COMMENT self-review, not independent human APPROVE.
- Owner explicitly authorized planning, implementation and merge in the task. Plan and implementation were initially submitted as separate Draft PRs, reviewed/CI checked and marked Ready before their authorized merges.
- Implementation merge: `e74d343e3ebe4fd4aa9b44405a75ee74f74f798f`.
- [Exact post-merge Publisher CI39741175076](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39741175076): push to develop at the implementation merge SHA, completed/SUCCESS. [Recorded verification](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/68#issuecomment-6335387892).

## Executed exact-merge checks

| Environment | Job | Full suite | Total coverage | PDF batch gate | HTML batch gate |
| --- | --- | --- | --- | --- | --- |
| Ubuntu / Python 3.13 | [119698487176](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39741175076/job/119698487176) | 762 passed | 99.92% | 100% | 100% |
| Ubuntu / Python 3.14 | [119698486927](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39741175076/job/119698486927) | 762 passed | 99.92% | 100% | 100% |
| Windows / Python 3.13 | [119698487212](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39741175076/job/119698487212) | 757 passed, 5 skipped | 99.92% | 100% | 99.04% |
| Windows / Python 3.14 | [119698487211](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39741175076/job/119698487211) | 757 passed, 5 skipped | 99.92% | 100% | 98.99% |

Hosted CPython versions are3.13.16/3.14.8. Exact-merge logs record common
rendering/runtime versions: reportlab4.5.1, markdown-it-py4.2.0,
python-docx1.2.0, pydantic2.14.1, PyYAML6.0.3 and pillow13.0.0;
host/dev verifier pypdf6.21.2. Test/tool versions: pytest9.1.1,
pytest-cov7.1.0, coverage7.16.2, Ruff0.17.1, Black26.10.1, MyPy2.4.0.
Fresh wheel installs only runtime dependencies; pypdf is host/dev-only.

All four jobs succeed. Five Windows skips are case-sensitive collision cases;
Linux executes them. Hosted symlink cases execute. All ten independent >=95%
gates retained: domain, jobs, pipeline, orchestration, html_pipeline,
batch_pipeline, docx_pipeline, pdf_pipeline, docx_batch_pipeline,
pdf_batch_pipeline. All except HTML batch as tabulated are100%. Total>=99% passes.

Executed .github/workflows/ci.yml: python -m ruff check ., python -m black
--check ., python -m mypy src, full python -m pytest, full coverage
--cov=bgdxpublisher --cov-fail-under=99, ten package coverage commands
--cov-fail-under=95, pip wheel . --no-deps --wheel-dir dist-review,
fresh installed-wheel CLI/API/semantic checks and configured visual generation.
Existing smoke blocks/coverage gates/preview uploads are retained.

Local results remain distinct in [IMPLEMENTATION-EVIDENCE.md](IMPLEMENTATION-EVIDENCE.md):
Windows Python3.13.14 full697passed/65filesystem skips,total99.72%
(2459statements/7missing), new67cases52passed/15filesystem skips, new CLI adapter
43statements100%; Ruff/Black121files/MyPy67sources PASS. Full isolated installed
CI block PASS/exit0, including all actual CLI/API smoke and host PDF semantics.
The initial no-build-isolation missing setuptools backend was resolved with the
normal isolated build; example __notes__ assertion typo fixed before PR head.
Neither required a production correction. Historical wheel SHA256 retained in
implementation evidence; no new local production test/build run is claimed by
this documentation submission.

## Installed command and PDF equivalence

New examples/pdf_batch_cli_pipeline.py is copied outside checkout into a fresh
runtime-only wheel installation, source PYTHONPATH removed, invoked under -I
with installed-import assertion. It invokes the actual installed
publish-pdf-batch executable: success/mixed/all/refusal/overwrite/read/glyph/
preflight/parser/help/config and safe diagnostics, source/previous bytes and
injected expected/unexpected runtime-stop cases. Existing installed CLI/API
smoke checks continue to pass.

Existing host/dev-only examples/pdf_batch_verify.py compares those CLI PDFs with
direct batch API equivalents: page count/order/A4/text/decoded content streams,
complete dereferenced resources/fonts/embedded data, metadata/catalog language/
URI semantics. Only existing observed CreationDate/ModDate/trailer ID volatility
and stream transport normalization are excluded; no whole content/resource/font
section is discarded. No new runtime pypdf dependency.

## Actual exact-merge CLI visual inspection

Downloaded [pdf-batch-cli-preview artifact12409078913](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39741175076/artifacts/12409078913)
from the exact implementation merge run. ZIP SHA256 checked against API digest:
`bbcb505a33c230dcf42c282d452d21f629b25531f88029d170542d80ef5e4a36`.

Two distinct outputs are produced by the actual CLI: published/sample.pdf
(one page) and published/multipage.pdf (three pages). CI rasterizes both with
pdftoppm at90dpi. Actually opened ALL four PNGs: sample-page-1.png,
multipage-page-1.png, multipage-page-2.png and multipage-page-3.png.
Latin diacritics/Cyrillic, headings, bold/italic, nested/numbered lists, quote,
code, link and multipage flow are readable with no visible clipping/overlap.
Claim is limited to these two samples/four pages; not every input/viewer.

This adds exact-merge inspection beyond the earlier head/push artefact12408822892
reviewed before merge. Other configured DOCX/PDF/single/batch API/CLI previews
are retained/passing; no new manual inspection of those artifacts is claimed.

## Acceptance mapping and limits

[AC-01 through AC-09](ACCEPTANCE.md) PASS; AC-10 implementation review/owner
execution authorization/merge/exact CI complete. Final closure administration
remains pending below.

- AC-01: only new cli/pdf_batch.py and app.py import/subparser production changes.
  Path source/required output-dir, overwriteFalse/configNone/langund, validated
  language and allow_abbrev=False for the new parser. Invalid/unsupported/missing
  arguments exit2 and help0 before runtime. One registered batch service/exact
  BatchPdfRequest call; CLI never rescans or renders/writes individual files.
- AC-02/03: service order, COMPLETED-only Published lines and derived exact
  Batch complete summary. All stdout buffered until successful runtime stop;
  allsuccess exit0, mixed/all expected failures exit1. Failed cleanup never
  Published even if its committed file remains. Ordinal includes all items.
- AC-04/05: exact safe Failed: item=N PDF_PUBLICATION_FAILED stage=... and
  Batch publication failed: BATCH_PDF_PREFLIGHT_FAILED. Preflight has no stdout
  or fabricated counts. INFO logs omit raw path/name/body/cause/glyph details.
  Explicit success/API paths and internal API cause remain intentional data;
  parser/runtime/config message details are outside safe-publication guarantee.
  Existing batch preflight/snapshot/aliases/symlinks/collisions/refusal/overwrite,
  atomic writes, source/previous bytes and all direct/single/legacy APIs preserved.
- AC-06: all18body/stop combinations, startup states/constructor/config routing,
  stop once and primary identity tested. Expected stop error emits Runtime cleanup
  failed: <runtime error>, retains prior item/preflight diagnostics, suppresses
  all buffered stdout and returns1 absent unexpected primary. Active unexpected
  primary survives unexpected stop with one fixed safe note An unexpected runtime
  cleanup failure occurred.; without active primary, unexpected stop propagates
  itself. Real unexpected child stops later work and retains earlier commits.
  Registered child cleanup is FAILED/stage=cleanup/output=None/file retained/
  continue; writer cleanup stays write. No rollback/concurrent isolation promise.
- AC-07/08: exact-merge fresh installed command, host semantic and actual ALL-page
  CLI visuals described above.
- AC-09: four environments/full/static/coverage/build pass. Current user docs,
  examples/changelog/release guide match development status, errors and lifecycle.
  Existing renderer/fonts/writer/engine/runtime/CLI adapters/dependencies/version
  remain unchanged. Package remains1.1.0 until separate release preparation.

## Administrative disposition

This record supersedes historical pending review/CI/visual dispositions in
IMPLEMENTATION-EVIDENCE.md and planning VERIFY.md without rewriting original
results. Final closure-document formal review/owner acceptance, separately
explicitly authorized documentation merge and its exact post-merge CI must precede
issue #67 completion. This Draft submission performs none of those later actions.

SPR-023 supplies the last planned feature in the accepted1.2.0 CLI/API matrix.
That does not establish release readiness/publication: accepted closure, final
cross-format release-candidate/documentation/version/package acceptance and
explicit publication authorization remain required. No new feature scope added.
No production/main/version/dependency/release/tag changes or branch deletion in
this documentation submission. Main remains
`9883eca15ef4642db6513efa4fa3610158312f27`.
