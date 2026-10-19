# SPR-018 Implementation Evidence

Status: implemented for review, 2026-10-19; issue #47 open, no merge/closure.
Baseline: develop `97e57f643c4a05f0244a65363850d8f18eb6cdaf`, approved plan PR #46.

## Implementation and acceptance mapping

New pdf_pipeline package mirrors existing pipeline composition, with immutable
typed snapshots, fixed PDF_PUBLICATION_FAILED error and consistent result envelope.
Runtime adds only a registration alongside legacy PdfPublishingService.
CLI/parser, direct legacy API, PdfRenderer/fonts/shared writer and engines are
unchanged. No dependency/version change. Tests do not remove prior regressions.

| AC | Prepared evidence (final review pending) |
| --- | --- |
| 01–02 | test_equivalence: result/history/stages/invariants; single-operation and fresh-ID/no-fallback tests; immutable snapshots in source. |
| 03 | Metadata/path cases forbid reading before validation; same path/hardlink/parent/extension/overwrite/symlink cases retained. |
| 04–05 | Twelve UTF-8/BOM × metadata × empty/complex/multipage cases compare page count/order/A4, extracted text, decoded page content streams, title/lang, URI rects/targets and font resources. No byte equality or XML/PDF normalization. Source unchanged. |
| 06 | Existing PDF renderer safety tests retained; new glyph/control/font/LayoutError cases assert safe render stage/internal cause and previous bytes. |
| 07–08 | No-overwrite race, replace/flush failure and postcommit cleanup/context tests; cleanup once, FAILED/no result and committed file retained. Shared writer permission tests retained. |
| 09 | Safe logs/string and internal cause-chain tests, sentinel paths/title/body/cause exclusion. Legacy direct API and CLI diagnostics preserved. |
| 10 | Legacy API/CLI selection spy, direct contract regression, new runtime resolution/generic engine and caller-owned stop tests; existing PDF-first regression retained. |
| 11 | Fresh local installed-wheel example completed outside checkout; CI adds isolated copied example and host pypdf checks. Distinct new-API single/multipage preview added; actual CI artifact inspection pending. |
| 12 | Local checks below; eight independent gates configured, final-head four-environment CI and source review pending. |

New test path: tests/pdf_pipeline/test_pdf_publication.py, 42 cases. Existing
tests/publishing/test_pdf.py and all other tests remain unchanged.

## Executed local verification

Windows / Python 3.13.14, dedicated development environment:

- `python -m pytest tests/pdf_pipeline tests/publishing/test_pdf.py -q`: 66 passed,
  1 skipped (local PDF pipeline symlink privilege).
- `python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99 -q`:
  506 passed, 5 skipped; 99.86%, 2164 statements/3 missed.
- `python -m pytest tests/pdf_pipeline --cov=bgdxpublisher.pdf_pipeline --cov-report=term-missing --cov-fail-under=95 -q`:
  41 passed, 1 skipped; PDF pipeline 100%, 104 statements/0 missed.
- Ruff passes; Black checks 102 files; MyPy checks 61 source files; diff check passes.

Each pytest command used a distinct explicit basetemp under .pytest_cache after
creating its parent. Full-suite local skips: batch case-sensitive collision,
batch directory symlink and HTML/DOCX/PDF output symlink privileges. Linux CI must
execute these cases. Initial missing basetemp parent and unsupported-glyph test
fixture were corrected before the successful results above; no renderer change.

Wheel 1.1.0 built with unchanged dependencies, SHA-256
`400dd859030f9e038257ed17b1ecab2062a7ed046008a5d2d6f73375ce2cda32`.
Fresh venv installed this wheel; copied examples/pdf_pipeline.py ran with isolated
Python (-I) outside checkout and asserted installed site-packages imports,
COMPLETED result/bytes, fresh job, refusal/overwrite and safe read failure with
previous output retained. It generated one-page and five-page samples. Host pypdf
verified Unicode extraction and title/language; pypdf is not a runtime dependency.

## Pending disposition

CI exact-head results and actual API artifact page inspection will be recorded in
the PR before handoff, superseding these pending items without rewriting local
results. Formal review, separately authorized merge, exact post-merge acceptance
and closure remain required before completing #47. No main change/release/tag or
branch deletion.
