# SPR-019 Implementation Evidence

Status: implemented for review, 2026-10-20; issue #51 open, no merge/closure.
Baseline: approved plan PR #50 merge `50b39f3ee81c27ab3d601662d487b7d1dd977187`.

## Scope and acceptance mapping

Only src/bgdxpublisher/cli/publish.py changes production behavior: registered PDF
pipeline once/exact request/result.publication, typed safe error handling and
existing unexpected-primary protection extended to PDF (including both flags).
DOCX protection remains; HTML/batch/default behavior and PDF-first retained.
No direct API, renderer/fonts/writer, runtime registration, engine/orchestration,
dependency or version changes. Existing tests retained except obsolete PDF CLI
route assertions replaced with direct API diagnostic/cause/logging regression;
PDF-first test now spies pipeline service while forbidding DOCX.

| AC | Evidence prepared for formal review |
| --- | --- |
| 01 | Existing parser tests and test_parser_failure_never_initializes_runtime; app.py/signature unchanged. |
| 02–04 | Twelve test_pdf_routing_and_equivalence combinations capture exact request and forbid fallback; compare page order/count/A4/text/content streams/title/lang/link rects/targets/fonts and source bytes; existing both-flags spy. No broad normalization or whole-file byte equality. |
| 05–06 | Injected read/render/write errors; seven real missing/extension/encoding/glyph/control/font/layout cases; safe primary-line/log separation; parser exit 2. |
| 07–08 | Existing PDF pipeline race/alias/symlink/permissions/precommit tests retained; new CLI postcommit cleanup failure retains file/no success; existing cleanup-once/context isolation retained. |
| 09 | Twelve both-flags × success/typed/unexpected primary × expected/unexpected stop combinations assert exact adapter order/count/propagation, calls once and retained output; two startup cases. |
| 10 | Direct legacy result regression retained plus cause/glyph-code/logging test without redirection; pipeline API unchanged; DOCX/HTML matrix and full other-command suite retained. |
| 11 | Expanded actual installed executable workflow checks outside checkout, removed source PYTHONPATH, retained API smoke and previews. Actual final-head CI visual inspection pending. |
| 12 | Local checks below pass; existing eight gates unchanged; final-head four-environment CI, formal review and post-merge acceptance pending. |

New tests: tests/cli/test_pdf_cli_pipeline.py (26 cases) and
tests/cli/test_pdf_runtime_precedence.py (14 cases). Adapter diagnostics are counted
and ordered separately from allowed safe pipeline logs. New error strings omit
raw cause/glyph detail; legacy direct API retains it. Handled typed failure plus
unexpected stop propagates stop; active unexpected PDF primary survives unexpected
stop with fixed safe note. No rollback is promised for committed files.

## Executed local checks

Windows / Python 3.13.14:

- Focused approved-plan paths: 113 passed, 1 skipped (PDF output symlink privilege).
- Full suite with total coverage >=99%: 546 passed, 5 skipped; 99.86%,
  2165 statements/3 missed; cli/publish.py 100% (48 statements).
- Full-suite local skips: batch case-sensitive collision, batch directory symlink,
  HTML/DOCX/PDF output symlink privilege. Linux CI must run these cases.
- Ruff passes; Black checks 104 files; MyPy checks 61 source files; diff-check passes.

Commands: VERIFY.md focused pytest list and full pytest
--cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99; each used separate
explicit basetemp under prepared .pytest_cache. Initial new tests were refined to
distinguish permitted safe pipeline logs from exact primary diagnostics; results
above are the successful completed runs, not failed assertion attempts.

Wheel 1.1.0 SHA-256
`c8f55b2040406408aac2428a741607d2e3ac00c0dbb233a5f6b0255a66a26f78`.
Built with unchanged dependencies. Full Test installed wheel outside repository
workflow step completed locally: PASS against a fresh venv with source PYTHONPATH
removed and isolated host runner (-I). Actual PDF executable checks success,
metadata/Unicode, refusal/overwrite, parser rejection and safe validate/read/render
failures; all retained API and other-command checks also pass.

## Pending disposition

Exact-head CI and actual migrated-CLI pdf-preview inspection will be recorded in
PR evidence before handoff and supersede pending CI/visual items here. Formal
review, separately authorized merge, exact post-merge CI and accepted closure
remain required before completing #51. No main change/release/tag/branch deletion.
