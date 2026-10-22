# SPR-022 Acceptance and Closure Evidence

Verified 2026-10-22 on merged develop
`7d636e8224277ae4f3e84e116f5554fcd536ab39`. Technical implementation acceptance
passes; closure documentation submitted for review. Administrative closure remains
pending and [issue #63](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/63)
stays open. No batch PDF CLI is introduced by SPR-022.

## Provenance

- Approved plan [PR #62](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/62), baseline `9a79e256df0db1b8c1d2c264e5906792ff132c52`; exact plan CI39586733530 successful before implementation.
- Implementation [PR #64](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/64), reviewed head `e1d62a6bfbc1959614de9a11f94cbde9b0047c4e`.
- [Formal implementation review](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/64#pullrequestreview-5610173555): no blocking findings. Disclosed Codex COMMENT, not independent human APPROVE.
- Owner authorized Ready for review and merge in this task after the formal review. PR transitioned out of Draft before merging into develop.
- Implementation merge: `7d636e8224277ae4f3e84e116f5554fcd536ab39`.
- [Exact post-merge Publisher CI39735440229](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39735440229): push to develop at that merge SHA, completed/success. [Recorded post-merge verification](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/64#issuecomment-6334641619).

## Executed exact-merge quality checks

| Environment | Job | Full suite | Total coverage | PDF batch gate | HTML batch gate |
| --- | --- | --- | --- | --- | --- |
| Ubuntu / Python 3.13 | [119679908212](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39735440229/job/119679908212) | 695 passed | 99.92% | 100% | 100% |
| Ubuntu / Python 3.14 | [119679908564](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39735440229/job/119679908564) | 695 passed | 99.91% | 100% | 100% |
| Windows / Python 3.13 | [119679908460](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39735440229/job/119679908460) | 691 passed, 4 skipped | 99.92% | 100% | 99.04% |
| Windows / Python 3.14 | [119679908414](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39735440229/job/119679908414) | 691 passed, 4 skipped | 99.91% | 100% | 98.99% |

All four jobs succeed. Windows skips four case-sensitive collision cases; Linux
executes them. Hosted symlink checks execute. All ten independent >=95% package
gates pass: domain, jobs, pipeline, orchestration, html_pipeline, batch_pipeline,
docx_pipeline, pdf_pipeline, docx_batch_pipeline and pdf_batch_pipeline. All except
HTML batch as tabulated are 100%; full suite total >=99% retained.

Executed .github/workflows/ci.yml commands: python -m ruff check .,
python -m black --check ., python -m mypy src, python -m pytest,
full coverage --cov=bgdxpublisher --cov-fail-under=99, ten independent package
coverage commands --cov-fail-under=95 (new tests/pdf_batch_pipeline with
--cov=bgdxpublisher.pdf_batch_pipeline), pip wheel . --no-deps --wheel-dir
dist-review, fresh installed-wheel smoke/host semantic verification and configured
visual generation/uploads. New package cases: Ubuntu43passed; Windows42passed/
1case-collision skip, package100% on all four jobs.

Historical local Windows Python3.13.14 results remain distinct in
[IMPLEMENTATION-EVIDENCE.md](IMPLEMENTATION-EVIDENCE.md): full645passed/50filesystem
skips,total99.71%; new28passed/15filesystem skips,97.87%; Ruff/Black/MyPy pass.
Formal-review targeted rerun of tests/pdf_batch_pipeline, tests/pdf_pipeline,
tests/publishing/test_pdf.py, tests/cli and tests/runtime:329passed/31skipped,
25.88s. No new local code tests or wheel build are claimed by this documentation
submission. Exact-merge hosted checks establish integration proof.

Fresh wheel smoke runs outside checkout with PYTHONPATH removed, installed-import
assertion and copied examples/pdf_batch_pipeline.py under -I. The example uses
runtime dependencies only; host/dev-only examples/pdf_batch_verify.py uses pypdf
for semantic comparison. Success/mixed/all failures/refusal/overwrite/preflight/
read/glyph statuses and counts, source bytes and fresh IDs are checked. All
existing actual installed CLI/API smoke checks and previews remain passing.

## Actual exact-merge PDF visual inspection

Downloaded [pdf-batch-preview artifact12407157955](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39735440229/artifacts/12407157955)
from the exact merge run above. ZIP SHA256 checked against GitHub API digest:
`32974a7dd365590d9219035d7214a10c3f7a0bea345e5773317c5587d4bad322`.

The installed new API example generates distinct sample.pdf (1page) and
multipage.pdf (3pages), together with individual-API comparison outputs. CI
rasterizes the new batch outputs with pdftoppm. Actually opened ALL four PNGs:
sample-page-1.png and multipage-page-1.png, multipage-page-2.png,
multipage-page-3.png. Latin diacritics/Cyrillic, headings, bold/italic, nested and
numbered lists, quote, code, link and multipage flow are readable, without visible
clipping/overlap. Claim is limited to these two samples and four pages.

Other exact-merge retained artifacts: docx-preview12407028174,
pdf-preview12406863605, pdf-pipeline-preview12407038197,
docx-batch-preview12407163058 and docx-batch-cli-preview12407132975. Their configured
generation/upload steps pass; no new manual inspection of those artifacts is
claimed. This record adds exact-merge inspection beyond the earlier PR-head
artifact reviewed before merge.

## Accepted behavior and AC disposition

[AC-01 through AC-11](ACCEPTANCE.md) PASS; AC-12 technical/quality/documentation
and implementation review/authorization/merge/CI portions PASS. Final closure
administration remains pending as described below.

- AC-01: frozen/slotted typed request and terminal item/aggregate invariants,
  nonempty unique mapping and derived counts tested.
- AC-02/03/07: preflight validates language, source root before symlink resolution,
  immediate regular .md/.MD selection, stable casefold/name ordering, one frozen
  snapshot, empty/casefold collisions and every planned destination before mkdir
  or child publication. Symlinks/dangling links/directories and aliases/hardlinks
  to any selected input are rejected in both overwrite modes. Ordinary regular
  output refusal is per-item; safe same-directory output is allowed. Directory
  setup failure starts no child; partial mkdir is not rolled back. Atomic
  race/permission/flush/replace/temp policies retain existing tests.
- AC-04: new service composes the exact runtime-registered PdfPublicationService,
  once per selected source with exact PdfRequest and fresh job/document/context.
  No legacy fallback; batch does not start/stop runtime.
- AC-05: source bytes and PDF semantics match individual API requests: page
  count/order/A4/text/decoded content, complete dereferenced resources/fonts,
  metadata/catalog language/URI action/rectangle/subtype. Only observed
  CreationDate/ModDate/trailer ID volatility is excluded from cross-render
  equality; clock-shift test verifies those differences while content matches.
  Stream transport fields Length/Filter/DecodeParms are normalized to decoded
  bytes; no content/font/resource/metadata section is wholesale excluded.
- AC-06/09: expected PdfPublicationError retains ordered terminal result and
  continues later eligible items for mixed/all/refusal/read/title/glyph/control/
  font/layout/render/write failures. Fixed safe BATCH_PDF_PREFLIGHT_FAILED
  preserves internal cause; child stage/code remain structured. New logs/error
  strings omit raw paths/names/title/body/PDF bytes/cause. Explicit API result
  paths and cause are intentional data; legacy and unexpected external errors
  are outside this sanitization claim. PDF_PUBLICATION_FAILED is the wrapper
  code, not a replacement for the pipeline's failure code.
- AC-08: registered postcommit cleanup yields FAILED/stage=cleanup/output=None,
  retained file/failed count/continue/cleanup once. Writer cleanup stays write.
  Unexpected external primary propagates and stops later children; earlier
  committed files remain. No rollback or arbitrary concurrent isolation promise.
- AC-10: production changes confined to new pdf_batch_pipeline and runtime
  import/registration. Existing CLI/direct and batch APIs, single pipelines,
  renderer/fonts/writer/generic engine/lifecycle and dependencies/version retain
  their contracts and regressions. Batch PDF CLI belongs to future SPR-023.
- AC-11: exact-merge installed distribution, semantic verification and all-page
  new API visual evidence are recorded above.

## Administrative disposition

Implementation formal review, owner execution authorization, implementation merge
and exact post-merge CI are complete. This record supersedes historical pending
review/merge/CI/visual dispositions in IMPLEMENTATION-EVIDENCE.md and planning
VERIFY.md without rewriting their original results.

Final closure-document formal review/owner acceptance, separately authorized
documentation merge and exact documentation post-merge CI must precede completing
issue #63. This submission keeps it open and performs none of those later actions.
SPR-022 contributes to the accepted release1.2.0 scope; that edition is not yet
published or declared complete. No implementation, release/tag/version/dependency
change or branch deletion in this documentation submission. Main remains
`9883eca15ef4642db6513efa4fa3610158312f27`.
