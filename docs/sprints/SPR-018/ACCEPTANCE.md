# SPR-018 Acceptance Criteria

Status: technical AC-01–AC-12 PASS on merged develop `e5505be5b3f3e12a2bceebbb471ca79ddca14c19`, verified 2026-10-19. Closure documentation submitted for review; see [CLOSURE.md](CLOSURE.md).

| ID | Criterion | Required evidence |
| --- | --- | --- |
| AC-01 | Typed public contracts | Frozen consistent COMPLETED envelope; reject mismatched/failed results; typed FAILED error with fixed code/internal cause and no partial output. |
| AC-02 | Fresh jobs and stages | Independent IDs/context per call, exact order/status history, one read/render/write, no legacy fallback. |
| AC-03 | Validate before reading | Metadata/extension/source/directory/same path/hardlink/symlink/parent/overwrite cases; forbidden read/render/write spies. |
| AC-04 | Input/metadata fidelity | UTF-8/BOM, empty/complex/multipage, Latin/Cyrillic, default/custom title/lang; source unchanged. |
| AC-05 | PDF equivalence | Legacy/new page count/order/A4/text/metadata/lang/links/fonts comparisons; narrowly justified volatile-field handling, no raw-byte equality claim. |
| AC-06 | Safe content/render failures | Retained safe links/raw HTML/image-alt policy, embedded fonts, unsupported glyph/control/layout/font errors with render stage and internal causes. |
| AC-07 | Atomic filesystem protection | Refusal/overwrite, race/alias/symlink, precommit/flush/replace failures, previous bytes/temp cleanup and existing permissions tests retained. |
| AC-08 | Cleanup semantics | Postcommit FAILED/stage=cleanup/no successful result, file retained, cleanup once and distinct contexts; no rollback. |
| AC-09 | Safe diagnostics | Fixed PDF_PUBLICATION_FAILED and structured stage, sentinel path/title/body/bytes/cause absent from new logs/string; legacy diagnostics unchanged. |
| AC-10 | Registration/API/CLI compatibility | New service registered alongside legacy, generic runtime intact; both direct/CLI legacy contracts and PDF-first precedence unchanged; other commands pass regressions. |
| AC-11 | Wheel and actual visuals | Fresh installed API outside checkout validates outcomes; retained CLI smoke; inspect new-API single/multipage artifact including Unicode and code pagination. |
| AC-12 | Quality/review/closure | Four matrix jobs, total >=99%, eight independent >=95% gates; Ruff/Black/MyPy; formal review, explicit merge authorization, exact post-merge CI and acceptance/closure before issue completion. |

Record exact SHA, environments/dependencies, executed commands, counts/skips,
run/job/artifact links and actual inspection scope. New API safe diagnostics and
legacy CLI/direct raw diagnostics are separate contracts. No CLI migration accepted.

## Verified criterion mapping

Test names below refer to tests/pdf_pipeline/test_pdf_publication.py unless noted.

| AC | Result and supporting evidence |
| --- | --- |
| 01 | PASS: test_equivalence checks frozen/mismatched envelopes and rejects error from completed execution; stage failure tests reject successful result from FAILED execution and verify cause chain. |
| 02 | PASS: stage/history assertions; test_runtime_and_single_operations, fresh-ID/no-fallback and cleanup/context tests. |
| 03 | PASS: test_invalid_metadata_preserves_files, eight test_invalid_paths cases and output symlink; forbidden read confirms validation first. |
| 04–05 | PASS: twelve UTF-8/BOM × default/custom metadata × empty/complex/multipage comparisons; page order/count/A4/text/content streams/title/lang/URI rects/targets/fonts and source bytes, no broad normalization/raw-byte equality claim. |
| 06 | PASS: unchanged renderer and existing tests/publishing/test_pdf.py safety/font/layout regressions; four test_render_failure_boundaries cases retain bytes and safe render failure/cause. |
| 07 | PASS: race/replace/fsync failure tests preserve previous bytes/temp policy; inherited shared writer permissions regressions retained. |
| 08 | PASS: test_postcommit_cleanup_and_context_isolation: FAILED/stage=cleanup/output=None, committed PDF retained, cleanup once and distinct job/context per call. |
| 09 | PASS: safe message/log and stage failure cause-chain/sentinel tests; fixed document metadata and safe new-route diagnostics. Legacy raw diagnostics remain unchanged. |
| 10 | PASS: new registration alongside legacy; test_legacy_direct_api_retains_contract, test_cli_retains_legacy_route, generic runtime and caller-owned stop tests; existing PDF-first and all other regressions retained. |
| 11 | PASS: isolated installed-wheel API and retained CLI checks in all four jobs; actual six-page exact-merge API artifact inspection recorded in CLOSURE.md. |
| 12 | PASS technically: formal review, explicit owner acceptance/merge authorization and exact post-merge CI 39244005897; four jobs/total >=99%/eight independent >=95% gates. Administrative closure-document acceptance/merge/CI pending. |

Issue #47 remains open pending the administrative sequence in CLOSURE.md.
Successful implementation acceptance does not imply closure-document acceptance.
