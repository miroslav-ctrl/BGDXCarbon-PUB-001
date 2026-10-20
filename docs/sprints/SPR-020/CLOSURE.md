# SPR-020 Acceptance and Closure Evidence

Verified 2026-10-20 against merged develop
`676d84e4e463156e38824eb8e397f8ef819b0919`. Technical implementation acceptance
passes; closure documentation submitted for review. Administrative closure is
pending; issue #55 remains open.

## Provenance

- Approved plan [PR #54](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/54), implementation baseline `5a1e2816f3d01fdbeb22c24298db2f1a81ac3f21`.
- Implementation [PR #56](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/56), reviewed head `3fbb4ae124f717724e5c7efb05f2bc66c0b94137`.
- [Formal implementation review](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/56#pullrequestreview-5581611297) recorded no blocking findings. This was a disclosed Codex COMMENT, not an independent human APPROVE.
- Owner accepted the review, authorized Ready for review, then separately authorized merge into develop in this task.
- Implementation merge: `676d84e4e463156e38824eb8e397f8ef819b0919`.
- [Exact post-merge Publisher CI 39382395583](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39382395583) completed/success, push to develop at that merge SHA.

## Executed exact-merge CI

| Environment | Job | Full suite | Total | DOCX batch gate | HTML batch gate |
| --- | --- | --- | --- | --- | --- |
| Ubuntu / Python 3.13 | [118494237211](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39382395583/job/118494237211) | 586 passed | 99.91% | 100% | 100% |
| Ubuntu / Python 3.14 | [118494237004](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39382395583/job/118494237004) | 586 passed | 99.91% | 100% | 100% |
| Windows / Python 3.13 | [118494236867](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39382395583/job/118494236867) | 584 passed, 2 skipped | 99.91% | 100% | 99.04% |
| Windows / Python 3.14 | [118494237165](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39382395583/job/118494237165) | 584 passed, 2 skipped | 99.91% | 100% | 98.99% |

All four jobs pass. Windows skips two case-sensitive collision cases (existing
HTML batch and new DOCX batch); Linux executes them. All symlink cases execute
in hosted CI. New dedicated suite: Ubuntu 35 passed; Windows 34 passed/1 collision
skip. Nine independent >=95% gates pass: domain, jobs, pipeline, orchestration,
html_pipeline, batch_pipeline, docx_pipeline, pdf_pipeline, docx_batch_pipeline.
All except HTML batch as tabulated are 100%; total >=99% retained.

Executed `.github/workflows/ci.yml` commands: Ruff check, Black check, MyPy src,
pytest full suite, full coverage --cov-fail-under=99, nine independent package
coverage commands --cov-fail-under=95, wheel build and actual installed-wheel
smoke. Four-job Python3.13/3.14 Ubuntu/Windows matrix and existing previews intact.
[VERIFY.md](VERIFY.md) preserves commands and historical local evidence:
566 passed/20 filesystem skips, total99.78%, dedicated20 passed/15 skips97.87%.
Formal review targeted rerun:103 passed/16 filesystem skips, Windows Python3.13.14.
These local results are not substituted for hosted counts.

Fresh temporary installed wheel runs outside checkout, removes PYTHONPATH and
executes copied examples/docx_batch_pipeline.py with -I/installed-import assertion.
Success/mixed/all failures/refusal/overwrite/safe preflight, ordered status/counts,
metadata/language, source preservation and all uncompressed OOXML members against
individual DOCX API pass. No XML fields excluded; ZIP container metadata ignored.
Existing orchestration/HTML/batch/DOCX/PDF API and actual CLI smoke checks retained.
Historical local wheel SHA256/dependency snapshot remains in VERIFY.md and PR #56
verification comment; no new local wheel build is claimed by this docs change.

## Actual exact-merge batch visual inspection

Downloaded [docx-batch-preview artifact 12245803019](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39382395583/artifacts/12245803019).
Verified ZIP SHA256 against artifact digest:
`f6ee2c7c8ba436fbd971620005d3cabe48c8730afe3abadb77da211577ee9c3f`.

The new installed API example generated published/notes.docx and report.docx.
LibreOffice rendered each to PDF; pdftoppm rasterized at100dpi. Actually opened
ALL pages: notes-page-1.png and report-page-1.png (two distinct documents, one
page each). Latin diacritics/Cyrillic, headings, quote, numbered/bulleted lists,
bold/italic/code and link are readable without visible overlap/clipping. Scope
is these two samples; no claim for every input/viewer. Existing docx-preview
12245778163, pdf-preview12245977401 and pdf-pipeline-preview12246625259 are retained
and generation/upload succeeds; no new manual inspection of those claimed here.

## Accepted contracts and limits

[AC mapping](ACCEPTANCE.md) covers AC-01 through AC-12. New production code is
src/bgdxpublisher/docx_batch_pipeline; runtime/application.py only adds import and
constructor registration using the registered DocxPublicationService. Immutable
request/item/tuple aggregate validates terminal matching outcomes, unique nonempty
mappings and derives counts. No parent batch job or engine changes.

Read-only preflight precedes mkdir/children: validate language, nonsymlink source
root before resolve, immediate regular case-insensitive .md selection, reject
candidate symlinks including dangling, stable (name.casefold(),name) snapshot,
casefold target-stem collisions and empty selection. Output root symlink/non-dir,
every planned output symlink (both overwrite modes), selected-input aliases and
destination directories are rejected. index.md and same input/output directory
are permitted when guards pass. Directory setup may partially create directories;
no directory rollback or arbitrary concurrent filesystem guarantee.

Each child gets exact DocxRequest(source,output,overwrite,None,language), fresh
job/document/context, once sequentially. Typed DocxPublicationError produces a
FAILED item and continues; ordinary existing regular output refusal is per-item
validate failure. Unexpected external child exceptions propagate and stop later
attempts, retaining earlier commits. Each output is independently atomic.
Postcommit registered cleanup failure is FAILED/stage=cleanup/output=None, file
retained, counted failed, later items attempted. Internal writer cleanup failure
remains write stage; cleanup once and context isolation retained; no rollback.

Expected preflight string/code is BATCH_DOCX_PREFLIGHT_FAILED, internal cause
inspectable; per-item safe DOCX_PUBLICATION_FAILED execution/stage metadata retained.
New logs omit raw paths/names/title/Markdown/bytes/cause. Explicit result paths are
caller-visible data; unexpected external exceptions retain propagation under the
approved contract. Existing single API diagnostics remain unchanged. Caller owns
initialize/start/finally-stop; batch service never stops runtime. All existing CLI,
direct APIs, renderer/fonts/writer/engine, dependencies and version remain intact.

## Administrative disposition

Implementation review, owner implementation acceptance, implementation merge and
exact post-merge CI are complete. This record supersedes pending implementation
review/merge/CI/visual dispositions in historical VERIFY.md without rewriting its
executed local results. Final closure-document formal review, owner acceptance,
separately authorized documentation merge and exact documentation post-merge CI
remain required before completing [issue #55](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/55).

This submission keeps issue open; it does not perform those later actions.
No merge, release/tag, dependency/version change or branch deletion. main verified
unchanged at `9883eca15ef4642db6513efa4fa3610158312f27`.
