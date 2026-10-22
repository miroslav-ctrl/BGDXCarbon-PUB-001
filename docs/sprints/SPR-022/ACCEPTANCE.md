# SPR-022 Acceptance Criteria

Status: technical implementation acceptance verified on merge
`7d636e8224277ae4f3e84e116f5554fcd536ab39`; see [final evidence](CLOSURE.md).
AC-01 through AC-11 PASS against exact-merge tests, installed distribution and
all-page visual evidence. AC-12 quality/documentation and implementation review/
owner authorization/merge/CI portions PASS; final closure-document review,
acceptance, authorized documentation merge/CI and issue #63 completion PENDING.
Historical [implementation mapping](IMPLEMENTATION-EVIDENCE.md) retains original
submission results; baseline/plan CI does not substitute implementation proof.

| ID | Criterion | Required evidence |
| --- | --- | --- |
| AC-01 | Immutable typed terminal aggregate | Request defaults/frozen fields, matching COMPLETED PublishResult/FAILED no output, tuple/empty/duplicate/nonterminal/mismatch guards and derived counts. |
| AC-02 | Read-only preflight | Invalid language/root/file/empty/collision/source symlink/dangling/output cases before mkdir/children; source root checked before resolve. |
| AC-03 | Deterministic source snapshot | Immediate regular .md/.MD only, stable sort/index.md allowed/nested ignore, capture once/no rescan after added input. |
| AC-04 | Registered single PDF reuse | Constructor inject registered single identity, exact PdfRequest/one call per source/no legacy fallback; fresh document/job/context per item/repeated run. |
| AC-05 | PDF semantic fidelity | Unicode/BOM/empty/single/multipage/different inputs; page/order/A4/text/decoded streams/fonts/resources/metadata/lang/URI semantics vs individual API; source preserved, only narrow justified volatility exclusions. |
| AC-06 | Mixed/all expected failures | Ordered terminal items/counts, refusal/overwrite/bad UTF-8/title/glyph/font/layout/render/write cases; typed failures continue, later eligible item succeeds and previous bytes preserved. |
| AC-07 | Filesystem and atomic protection | Every output symlink/dangling/unrelated/input alias/directory before mkdir/children/both overwrite modes; mkdir failure safe/no child, race/permission/flush/replace/temp policies retained. |
| AC-08 | Cleanup and unexpected propagation | Postcommit registered cleanup FAILED/stage=cleanup/outputNone/file retained/count failed/continue/once; writer cleanup stays write; unexpected external primary propagates/stops later items/earlier commits retained. |
| AC-09 | Safe diagnostics and explicit data | Fixed BATCH_PDF_PREFLIGHT_FAILED/cause, existing safe child metadata/code/stage, no raw input/path/name/title/body/bytes/cause in new logs/string; explicit result paths/cause boundary documented. |
| AC-10 | API/CLI/lifecycle compatibility | New runtime composition only, batch never owns stop; existing single/legacy/batch APIs and all commands/generic engine/writer/renderer/fonts untouched and regressions pass. |
| AC-11 | Installed distribution and actual visuals | Fresh isolated installed new API/runtime-only example + host pypdf; success/mixed/all/refusal/overwrite/preflight/glyph statuses/counts; >=2new API PDFs including multipage, ALL sample pages rendered/inspected with exact provenance. |
| AC-12 | Quality, documentation and closure | Four jobs,total>=99%,ten independent>=95% gates,static checks; current API docs/examples/release guide accurate. Formal review/owner acceptance/authorized merge/exact post-merge CI/accepted closure before issue completion; no main/release/version change. |

Record exact environment/dependencies/commands/SHA/run/jobs/counts/skips/artifact/
digest and actual manual page scope. No implementation issue created by this plan.
