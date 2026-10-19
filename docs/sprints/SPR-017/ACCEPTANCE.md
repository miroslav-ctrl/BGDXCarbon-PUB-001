# SPR-017 Acceptance Criteria

Status: all pending. A plan or successful baseline CI is not implementation evidence.

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
