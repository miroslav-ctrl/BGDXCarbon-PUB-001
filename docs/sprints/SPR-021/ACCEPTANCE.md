# SPR-021 Acceptance Criteria

Status: technical implementation acceptance verified on merge
`285d6ac5de8deb55105d96ed96f7dec3574b52d5`; see [final evidence](CLOSURE.md).
Final closure-document acceptance/merge and issue completion remain pending.

| ID | Required behavior | Verified evidence / disposition |
| --- | --- | --- |
| AC-01 | Thin new publish-docx-batch parser/dispatch | PASS: exact new subparser/defaults/help/config/lang/required args, abbreviations rejected before runtime; one registered batch call/exact request, no rescan/fallback. |
| AC-02 | Successful terminal projection | PASS: ordered Completed-only Published lines, exact derived summary/counts, buffered stdout emitted after successful stop, exit0 on all success. |
| AC-03 | Mixed/all failure projection | PASS: mixed/all failures exit1, ordinal counts all predecessors; exact safe per-item stage lines and summary; cleanup FAILED never Published. |
| AC-04 | Safe preflight and diagnostic boundaries | PASS: exact safe preflight code/no stdout/cause stringification; sentinel protection with actual INFO logs. Argparse/runtime/config details remain explicitly separate. |
| AC-05 | Preserve API/filesystem/rendering | PASS: direct APIs/old CLI/core unchanged; selection/refusal/overwrite/aliases/dangling/collisions and full uncompressed OOXML fidelity/source preservation tested. |
| AC-06 | Runtime shutdown and primary precedence | PASS: 18 body/stop combinations, startup states/stop once/constructor propagation/real unexpected child retained commit; exact stream order and primary identity/safe note, no rollback. |
| AC-07 | Installed distribution and existing commands | PASS: exact-merge fresh installed-wheel actual command/config/metadata/errors and injected shutdown checks; all existing installed CLI/API checks retained. |
| AC-08 | Actual CLI visual acceptance | PASS: exact-merge CLI artifact12334309696, verified ZIP digest; all2pages of2distinct actual CLI DOCX outputs inspected; other previews retained, scope in CLOSURE.md. |
| AC-09 | Quality and current documentation | PASS: four exact-merge jobs,total99.91%,nine>=95% gates; static/build checks and user docs/examples/changelog/release guide alignment; no version/dependency bump/history rewrite. |
| AC-10 | Formal review and final closure | Technical PASS: approved plan/authorization/formal review/owner acceptance/implementation merge/exact CI complete. Final closure-document review/acceptance/merge/post-merge CI and issue#59 completion PENDING. |

Record exact commits/environments/commands/dependencies/counts/skips/run/jobs and
actual manual inspection scope. Issue #59 stays open pending administrative closure.
