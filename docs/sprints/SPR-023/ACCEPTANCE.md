# SPR-023 Acceptance Criteria

Status: technical implementation acceptance verified on merge
`e74d343e3ebe4fd4aa9b44405a75ee74f74f798f`; see [final evidence](CLOSURE.md).
AC-01 through AC-09 PASS. AC-10 implementation review/owner authorization/merge/
exact CI complete; final closure-document review/owner acceptance, authorized
closure merge/exact CI and issue #67 completion remain PENDING. Historical
[implementation evidence](IMPLEMENTATION-EVIDENCE.md) retains submission results.

| ID | Required behavior | Evidence required |
| --- | --- | --- |
| AC-01 | New thin publish-pdf-batch parser/dispatch | Path source/required output-dir/defaults/config/lang; unsupported/abbreviated args exit2 and help0 before runtime; exact registered batch request once. |
| AC-02 | Success projection | Ordered COMPLETED-only Published lines + exact derived summary buffered until successful stop; exit0 only all succeeded. |
| AC-03 | Mixed/all failures | Ordered safe Failed item ordinal/PDF_PUBLICATION_FAILED/stage, later success and exact counts/exit1; failed cleanup never Published. |
| AC-04 | Preflight/safe diagnostics | Exact BATCH_PDF_PREFLIGHT_FAILED line/exit1/no stdout or synthetic counts; INFO logs omit raw input/name/content/cause/glyph data. Runtime/config/parser boundary explicit. |
| AC-05 | Preserve API/filesystem/PDF semantics | No batch/single/legacy API or writer/renderer change; preflight/alias/symlink/collision/refusal/overwrite/source-byte regressions and full semantic fidelity with narrow existing volatility exclusions. |
| AC-06 | Runtime close/primary precedence | 18 body/stop combinations, startup states/stop once/constructor propagation/real unexpected partial commits; exact output timing and original primary/safe note, no rollback. |
| AC-07 | Fresh installed distribution | Real installed CLI outside checkout/cleared PYTHONPATH, runtime-only example and host PDF verifier; success/mixed/all/refusal/overwrite/read/glyph/preflight/parser/config/stop checks, all existing smoke retained. |
| AC-08 | Actual CLI visual evidence | Two distinct actual CLI PDFs including multipage; render/open ALL pages; exact SHA/run/artifact/digest; existing previews retained. |
| AC-09 | Quality/docs | Four-env full/static/build/total>=99% and all10>=95% gates; current docs/examples/guide accurate; no version/dependency/history rewrite. |
| AC-10 | Formal acceptance/closure | Plan/implementation review, owner authorization, authorized merges and exact post-merge CI; accepted final closure before tracking issue completion. |
