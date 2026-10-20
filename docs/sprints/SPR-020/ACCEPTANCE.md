# SPR-020 Acceptance Criteria

Status: technical implementation criteria verified on merge
`676d84e4e463156e38824eb8e397f8ef819b0919`; see [closure evidence](CLOSURE.md).
Final closure-document acceptance/merge and issue completion pending.

| ID | Criterion | Verified evidence / disposition |
| --- | --- | --- |
| AC-01 | Typed immutable aggregate | PASS: frozen request/item/result, matching completed output/failed no output; tuple/empty/duplicate/nonterminal guards and derived counts tested. |
| AC-02 | Read-only preflight | PASS: invalid language/root/empty/collision/output and symlink/alias checks before mkdir/child calls; preflight parametrization and both overwrite modes. |
| AC-03 | Deterministic snapshot | PASS: immediate .md/.MD only, stable sort, index.md allowed, nested inputs ignored; adding a file during first child call does not rescan. |
| AC-04 | Single pipeline reuse | PASS: runtime registered-single identity, exact requests once per selected source, fresh job IDs/context across repeated calls; no legacy fallback. |
| AC-05 | DOCX fidelity | PASS: every uncompressed OOXML member/inventory vs individual API, no XML exclusions; Unicode/BOM/empty/different inputs and source preservation. |
| AC-06 | Partial/all failures | PASS: typed validate/read/render/write failures continue; ordered mixed/all failure counts, preserved refused bytes, later eligible successes and overwrite. |
| AC-07 | Filesystem protection | PASS: preflight/mkdir/symlink/hardlink/directory guards; atomic link race/replace/permission/fsync/temp failure injections; source and previous outputs retained. |
| AC-08 | Cleanup/unexpected failure | PASS: registered postcommit cleanup failed item/stage=cleanup/file retained/later continuation/once; external unexpected propagation/no later attempts/no rollback. |
| AC-09 | Safe diagnostics boundary | PASS: fixed BATCH_DOCX_PREFLIGHT_FAILED and inspectable cause; safe per-item stage/code/log sentinels. Explicit result paths and unexpected propagation remain intentional boundaries. |
| AC-10 | Runtime/API/CLI compatibility | PASS: new runtime registration reuses single service; caller owns lifecycle. Existing CLI/direct API/renderer/writer/engine unchanged and regressions/installed smoke pass. |
| AC-11 | Installed wheel/visuals | PASS: fresh installed-wheel scenario and exact-merge batch artifact12245803019; both actual pages inspected, SHA256 and scope in CLOSURE.md. |
| AC-12 | Quality/review/closure | Technical PASS: four jobs, total99.91%, nine independent gates pass, new package100%, static/wheel checks pass; implementation review/owner authorization/merge verified. Final documentation review/acceptance/merge/post-merge CI and issue closure PENDING. |

Record exact SHA/environments/dependencies/commands/counts/skips, run/job/artifact
links and actual page inspection scope. No new CLI behavior is accepted here.

Exact CI/job/count/skip/visual provenance is recorded in CLOSURE.md. No new CLI
behavior accepted; issue #55 remains open pending administrative closure.
