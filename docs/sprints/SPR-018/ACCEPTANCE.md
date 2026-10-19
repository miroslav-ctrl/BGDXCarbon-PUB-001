# SPR-018 Acceptance Criteria

Status: all pending. Baseline CI and approved plan are not implementation evidence.

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
