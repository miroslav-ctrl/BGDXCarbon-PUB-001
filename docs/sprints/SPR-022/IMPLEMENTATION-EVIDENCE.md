# SPR-022 Implementation Evidence

Submitted 2026-10-21 for Draft review; not final acceptance/closure.
Approved plan#62 merged at9a79e256df0db1b8c1d2c264e5906792ff132c52,
exact plan post-merge CI39586733530 SUCCESS all four environments before implementation.
Branch feature/spr-022-pdf-batch; [issue#63](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/63)
remains open until formal review/owner acceptance/authorized merge/exact post-merge
CI/accepted closure. No batch PDF CLI in this sprint.

## Executed local checks

Windows Python3.13.14, pytest9.1.1/pytest-cov7.1.0/coverage7.16.2:
full645passed/50filesystem skips,2408statements/7missing,total99.71% (>=99%).
New43cases:28passed/15skips (14symlink privilege cases/1case-sensitive collision),
package97.87% (94statements/2missing; >=95%). Existing35filesystem skips belong
to baseline; Linux CI must execute the filesystem-sensitive cases. Ruff passes;
Black117files unchanged; MyPy66source files passes. No dependency/version changes.

Commands: ruff check ., black --check ., mypy src; pytest tests/pdf_batch_pipeline
--cov=bgdxpublisher.pdf_batch_pipeline --cov-report=term-missing --cov-fail-under=95;
full pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99;
pip wheel . --no-deps --wheel-dir dist-review.

Local wheel bgdxpublisher-1.1.0-py3-none-any.whl SHA256
`2141ef76b748f9bd12c89147d1df8035dd8a1d633e0b5e3f035cf010bcfb7f6e`.
Full fresh installed-wheel CI block is executed separately outside checkout,
source PYTHONPATH removed/copied example -I: PASS, exit0 (including host semantic
checks and every retained actual CLI/API smoke). Exact-head CI/actual PDF page
review evidence recorded in PR. Existing actual CLI/API smoke
blocks retained, no new runtime pypdf dependency.

## AC mapping

- AC-01: frozen request/defaults/item/tuple/result/unique nonempty mappings and
  terminal completed-output/failed-no-output invariants, derived counts tested.
- AC-02/03/07: read-only preflight before mkdir/children, source root symlink
  before resolve, candidate dangling/output symlink modes, aliases/hardlinks/
  destination dirs/collisions/empty/language/mkdir failure tested. Stable frozen
  source order/index.md/nested ignore/new-input-no-rescan; safe same-directory
  output. Atomic race/replace/fsync/permission/temp unlink injections retained.
- AC-04: runtime registered single identity, exact PdfRequest once per selected
  source, fresh IDs/context across repeated calls; explicit legacy-forbidden test.
- AC-05: each batch PDF vs single API, page count/order/A4/text/decoded content,
  complete dereferenced resources/font streams/encoding semantics and metadata/
  catalog language/URI action+rectangle+subtype. Unicode/BOM/empty/rich/multipage,
  source bytes retained. pypdf comparison is tests/host-only.
- AC-06: real refusal/overwrite/mixed/all failed/read/glyph/control and injected
  title/font/TTFError/LayoutError/render/write failures; eligible later source
  succeeds. Legacy glyph diagnostic contract still exposes U+6F22, new logs do not.
- AC-08: registered postcommit cleanup FAILED/stage=cleanup/outputNone/file kept/
  failed count/continue/once/context isolation; internal writer cleanup stays write;
  unexpected external primary propagates/stops later attempts/earlier commit stays.
- AC-09: preflight fixed BATCH_PDF_PREFLIGHT_FAILED/code/cause, log sentinel safety,
  structured child failure metadata. Explicit result paths/internal causes are
  deliberate API data; unexpected external/legacy errors not claimed sanitized.
- AC-10: only new pdf_batch_pipeline and runtime import/constructor registration
  alter production. Existing CLI/direct/batch APIs/single pipelines/renderer/fonts/
  writer/engine/lifecycle unchanged; caller owns runtime finally-stop.
- AC-11: runtime-only examples/pdf_batch_pipeline.py, host/dev-only
  examples/pdf_batch_verify.py compares installed new outputs with individual API
  outputs. Actual success/mixed/all/refusal/overwrite/preflight/glyph/read/status/
  bytes checks; distinct new API single/multipage PDFs rasterized. All pages must
  actually be inspected; exact evidence is in PR once available.
- AC-12: tenth independent>=95% gate supplements unchanged existing nine,
  total>=99%/four-env/static checks; docs/examples/changelog/release guide aligned
  to development API/ten gates. Formal review/owner acceptance/authorized merge/
  exact post-merge CI/accepted closure pending.1.2.0 not published/complete.

## Narrow PDF comparison exclusions

ReportLab wall-clock CreationDate/ModDate and trailer ID are deliberately excluded
from cross-render equality. test_observed_reportlab_volatility moves its clock
120seconds and observes ALL THREE differing while semantic assertions pass.
All other metadata, decoded page streams and complete dereferenced page resource
values (including embedded font bytes) are compared. Stream transport-only Length,
Filter and DecodeParms are replaced by decoded stream bytes; object numbers,
compression and serialization are not PDF semantic differences. No content/font/
resource/metadata section is wholesale discarded. No renderer/font change needed.

No release/tag/main/CLI/version/dependency change or branch deletion. Actual
implementation Draft review is separate from final administrative closure.
