# SPR-019 Acceptance Criteria

Status: all pending. Planning/baseline CI is not implementation evidence.

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
