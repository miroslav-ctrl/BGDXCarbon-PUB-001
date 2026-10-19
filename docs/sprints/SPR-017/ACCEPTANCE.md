# SPR-017 Acceptance Criteria

Status: technical AC-01–AC-12 PASS on merged develop `d39b2904d3189326d01e0b1313f6e6c6bff24382`, verified 2026-10-19. Closure documentation submitted for review; see [CLOSURE.md](CLOSURE.md).

| ID | Criterion | Required evidence |
| --- | --- | --- |
| AC-01 | Parser/signature/defaults unchanged | Exact existing options; parser rejection exit 2 before runtime; no theme/TOC added. |
| AC-02 | New service selected once | Capture forwarded DocxRequest; forbid legacy DOCX publication fallback; PDF-first precedence retained for both flags. |
| AC-03 | Success contract retained | Exactly one Published stdout line after successful stop, exit 0, correct output path/bytes_written. |
| AC-04 | OOXML/source fidelity | Legacy/CLI package-member comparisons for UTF-8/BOM, empty/complex input, default/custom title/lang, Unicode and safety; source unchanged. |
| AC-05 | Safe validate/read/render/write failures | Exit 1, exact code/stage primary line, no Published stdout/raw paths/title/body/cause/traceback; safe logs allowed. |
| AC-06 | Parser vs operational distinction | Missing args/invalid options exit 2; nonexistent source/invalid output extension and operational failures exit 1. |
| AC-07 | Filesystem and overwrite protections | Refusal preserves previous bytes; explicit overwrite, aliases/symlinks/races/precommit cleanup; inherited permissions tests retained. |
| AC-08 | Postcommit cleanup semantics | stage=cleanup, FAILED/exit 1/no success stdout, committed file retained and cleanup once; no rollback. |
| AC-09 | Runtime lifecycle and precedence | Initialize/start once, finally stop as specified; primary + expected/unexpected shutdown combinations; exact diagnostic count/order, no masked primary or false success. |
| AC-10 | Direct APIs and other commands intact | Legacy DOCX API result/errors/logging unchanged, new API unchanged; HTML/PDF/batch/default runtime regression and precedence tests pass. |
| AC-11 | Installed wheel and visual review | Real publish-docx CLI outside checkout: success, refusal/overwrite, parser rejection and safe operational failures; retained API smoke and actual DOCX visual artifact inspection recorded. |
| AC-12 | Quality and review evidence | Four Ubuntu/Windows Python 3.13/3.14 jobs, total >=99%, seven independent >=95% gates, Ruff/Black/MyPy; review/authorization and exact post-merge CI. |

Record exact tested SHA, environments, commands, counts/skips, artifact/run links
and actual results. No source/merge/issue closure acceptance can be inferred from
planning. Legacy direct API diagnostic preservation and intentional CLI stderr
replacement are distinct contracts.

## Verified criterion mapping

| AC | Result and exact supporting evidence |
| --- | --- |
| 01 | PASS: cli/app.py and run_publish signature unchanged; test_cli_bad_arguments and test_parser_failure_never_initializes_runtime. |
| 02 | PASS: eight test_docx_routing_and_equivalence cases capture exact request/single call and forbid fallback; test_pdf_first_when_both_flags. |
| 03 | PASS: exact Published stdout assertions, result.publication adaptation and source review prove success after successful stop only; direct API bytes_written assertions retained. |
| 04 | PASS: eight UTF-8/BOM × metadata × empty/complex cases compare all uncompressed members and inventory without XML normalization; source bytes unchanged; shared safety/structure regressions retained. |
| 05 | PASS: test_safe_stage_errors, missing-source validation, postcommit cleanup, safe pipeline logs and real installed CLI read/validate errors; structured code/stage without raw cause. |
| 06 | PASS: parser invalid/missing arguments exit 2 before runtime; pipeline invalid paths/extension and installed missing/invalid UTF-8 source exit 1. |
| 07 | PASS: retained pipeline invalid-path/symlink/race/precommit and shared writer protection tests; installed CLI refusal/overwrite preserves bytes. |
| 08 | PASS: test_postcommit_cleanup_failure_retains_output and test_postcommit_cleanup_and_context_isolation; FAILED stage=cleanup, cleanup once, committed file retained. |
| 09 | PASS: expected shutdown combinations and init/start lifecycle tests; unexpected DOCX/HTML primary/shutdown matrix; source review confirms cleanup-before-primary order and no false success. |
| 10 | PASS: unchanged production direct APIs; test_legacy_direct_api_retains_contract, legacy error/bytes tests, new API fresh-job/no-fallback tests; full other-command regressions. |
| 11 | PASS: all four fresh installed-wheel jobs; actual exact-merge artifact 12177485556/page-1.png inspected as scoped in CLOSURE.md. |
| 12 | PASS technically: formal review, owner acceptance/merge authorization and exact post-merge CI 39231217588; all four jobs, total 99.90% and seven separate gates pass. Closure-document acceptance/merge remains administrative pending. |

Test paths: tests/cli/test_docx_cli_pipeline.py,
tests/cli/test_docx_runtime_precedence.py, tests/publishing/test_docx.py and
tests/docx_pipeline/test_docx_publication.py. [CLOSURE.md](CLOSURE.md) records
job IDs/counts, limits, visual evidence, review and remaining administrative steps.
Issue #43 remains open; this record does not claim its completion.
