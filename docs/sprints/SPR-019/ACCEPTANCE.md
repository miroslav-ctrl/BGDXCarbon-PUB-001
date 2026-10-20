# SPR-019 Acceptance Criteria

Status: technical AC-01–AC-12 PASS on merged develop `30a21a651cf3ed9153bda7d17f624b5210999248`, verified 2026-10-20. Closure documentation submitted for review; see [CLOSURE.md](CLOSURE.md).

| ID | Criterion | Required evidence |
| --- | --- | --- |
| AC-01 | Parser/signature/defaults retained | Existing options only; exact metadata diagnostics/exit 2 before runtime; no theme/TOC. |
| AC-02 | New PDF route once | Exact PdfRequest, single registered service call, no legacy fallback; PDF-first both flags. |
| AC-03 | Success contract | Exactly one Published line/exit 0 after successful stop, correct output and bytes_written. |
| AC-04 | PDF/source fidelity | UTF-8/BOM × metadata × empty/complex/multipage comparisons; page/text/geometry/metadata/lang/URI/font semantics and unchanged source. |
| AC-05 | Safe operational errors | Exit 1 with one exact PDF_PUBLICATION_FAILED stage line, no success stdout/raw content/path/cause/glyph detail/traceback; safe logs allowed. |
| AC-06 | Parser/operational distinction | Parser missing/invalid args exit 2; valid missing source/invalid extension exit 1 validate; encoding read, glyph/font/layout render, write/cleanup correctly distinguished. |
| AC-07 | Filesystem protection | Refusal preserves bytes; explicit overwrite and inherited aliases/symlinks/races/permissions/precommit temp cleanup. |
| AC-08 | Postcommit cleanup | FAILED/stage=cleanup/exit 1/no Published, committed file retained, cleanup once/context independence; no rollback. |
| AC-09 | Runtime and exception precedence | Init/start/stop states once; expected stop cleanup-before-primary ordering and count; active unexpected PDF primary retained on unexpected stop; unexpected stop without active unexpected primary propagates (including typed failure already handled). |
| AC-10 | APIs/other routes preserved | Legacy result/errors/cause/logging incl. glyph detail unchanged, pipeline API intact; DOCX protection/HTML/batch/default runtime and PDF-first regressions. |
| AC-11 | Installed wheel/actual visuals | Real CLI outside checkout: metadata/Unicode/refusal/overwrite/parser and safe validate/read/render failures; retained API smoke, actual CLI PDF artifact review and multipage API/DOCX checks. |
| AC-12 | Quality/review/closure | Four Ubuntu/Windows Python 3.13/3.14 jobs, total >=99%, eight independent >=95% gates, Ruff/Black/MyPy; formal review, explicit merge authorization, exact post-merge acceptance/closure before issue completion. |

Record tested SHA/environments/dependencies/commands/counts/skips, exact logs and
run/job/artifact/page links and inspection scope. Separate new CLI diagnostic
compatibility change from preservation of legacy direct API diagnostics.

## Verified criterion mapping

| AC | Result and supporting evidence |
| --- | --- |
| 01 | PASS: app.py/signature/defaults unchanged; existing parser tests and test_parser_failure_never_initializes_runtime. |
| 02 | PASS: twelve test_pdf_routing_and_equivalence cases capture exact request/one call and forbid legacy fallback; updated PDF-first both-flags spy forbids DOCX. |
| 03–04 | PASS: exact stdout after finally/stop, twelve UTF-8/BOM × metadata × empty/complex/multipage comparisons; page count/order/A4/text/content streams/title/lang/URI rects/targets/fonts/source bytes; direct bytes_written assertions retained. No broad normalization/raw whole-file equality. |
| 05–06 | PASS: injected stage errors and seven real missing/extension/encoding/glyph/control/font/layout cases; exact primary diagnostics counted separately from safe logs; parser exit 2 and operational stage/exit 1. |
| 07 | PASS: retained pipeline alias/symlink/race/permissions/precommit tests and actual CLI refusal/overwrite preserving bytes. |
| 08 | PASS: CLI test_postcommit_cleanup_failure_retains_output plus retained API cleanup once/context isolation/FAILED/no envelope tests. Committed PDF retained; no rollback. |
| 09 | PASS: twelve PDF both-flags/primary/stop combinations assert exact adapter line count/order/propagation/retained outputs and init/start/stop once; two startup cases; existing DOCX/HTML matrix retained. |
| 10 | PASS: unchanged direct APIs; retained result/overwrite regression plus test_legacy_direct_diagnostic_and_logging checks raw glyph code/cause/logging without redirection; full other-command tests. |
| 11 | PASS: actual installed-wheel CLI plus retained API smoke in all jobs; exact-merge migrated-CLI artifact 12244517111/page-1.png inspected; separate API multipage/DOCX generation/checks retained. |
| 12 | PASS technically: formal review and explicit owner acceptance/merge authorization; exact post-merge CI 39378245669, four jobs, total >=99%/eight independent >=95% gates. Administrative closure-document acceptance/merge/CI pending. |

Primary paths: tests/cli/test_pdf_cli_pipeline.py,
tests/cli/test_pdf_runtime_precedence.py, tests/publishing/test_pdf.py,
tests/pdf_pipeline/test_pdf_publication.py and tests/cli/test_docx_runtime_precedence.py.
Issue #51 remains open pending CLOSURE.md administrative sequence.
