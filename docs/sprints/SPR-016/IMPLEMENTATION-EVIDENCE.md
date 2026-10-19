# SPR-016 Implementation Evidence

Status: implemented for review, 2026-10-19. Issue #39 remains open.
Baseline: develop a8dff9c5535fd033fbb31e96b4fdc7e098d8e3cf, approved plan PR #38.
No merge or final acceptance claimed.

## Implementation

New docx_pipeline package exports DocxPublicationService, DocxPublicationResult and
DocxPublicationError. Immutable validate/read/render/write snapshots compose the
existing renderer, atomic writer, job service and execution engine. Each call has
fresh document/job/context identity. Safe code/stage/ID logs retain internal cause
chains without exposing user paths/title/body or raw failure messages.

Runtime registers the service alongside legacy DocxPublishingService. CLI routing,
legacy publisher/renderer code, dependencies, versions and other command routes
are unchanged. The new API is optional and does not replace publish-docx.

## Criterion mapping

Tests: tests/docx_pipeline/test_docx_publication.py (31 collected cases).

| AC | Evidence |
| --- | --- |
| 01 | test_equivalence rejects immutable/mismatched result and invalid error envelopes; test_stage_failure_chain_and_safe_logs checks failed envelopes and full cause chain |
| 02 | Exact stage/history assertions, test_new_api_never_calls_legacy_and_has_fresh_ids, test_postcommit_cleanup_and_context_isolation |
| 03 | Metadata/path cases include extension/parent/aliases/overwrite; forbidden ReadStage spies prove validation precedes reading |
| 04–05 | Eight UTF-8/BOM × default/custom metadata × empty/complex input comparisons; every uncompressed OOXML member matches legacy, with identical member sets and no XML normalization |
| 06 | Existing renderer unchanged; package comparison includes formatting/list/link/image/raw-HTML input, plus existing tests/publishing/test_docx.py safety/content regressions |
| 07 | test_no_overwrite_race_and_cleanup, test_precommit_write_failure_and_cleanup and real flush failure preserve bytes/temp cleanup; shared writer permission regressions retained |
| 08 | Injected read/render/write, invalid UTF-8 and cleanup failures; committed DOCX retained on cleanup failure with FAILED/no output; cleanup once per call |
| 09 | Captured logs exclude sentinel raw causes, source and content; document job metadata uses fixed safe strings |
| 10 | test_runtime_and_single_operations resolves both new orchestration and legacy runtime services; test_cli_keeps_legacy_route forbids new API invocation and checks unchanged success/refusal output |
| 11 | examples/docx_pipeline.py runs against installed wheel outside checkout; visual sample generation retained in CI, actual artifact review pending |
| 12 | Local results below; all seven independent coverage gates enforced in CI, four-environment results/review pending |

## Local verification

Windows / Python 3.13.14: full suite **443 passed, 4 skipped**; total coverage
**99.85%** (2051 statements, 3 missed). Independent DOCX package coverage:
**30 passed, 1 skipped / 100%** (104 statements). Skips are batch case-sensitive
collision, batch directory symlink privilege, inherited HTML output symlink and
new DOCX output symlink privilege. Linux CI must execute these cases.

Ruff passes; Black checks 96 Python files; MyPy checks 59 source files without
issues. git diff --check passes. Tests ran outside sandbox using an isolated
development environment. Initial test setup-path/assertion issues were corrected;
these figures describe completed successful runs.

Wheel 1.1.0 built and installed with runtime dependencies in a fresh venv.
SHA-256: e2afde27d9e75954d7178782218bafae606f6ae2cce1f9286b5a5e3a770c5c37.
Copied API example ran outside checkout with -I and empty PYTHONPATH; imports
assert site-packages. Exit 0 confirms runtime resolution, editable Unicode DOCX,
metadata, full OOXML-member equality to legacy, refusal/overwrite, independent job
IDs, invalid UTF-8 typed failure and preservation of source/previous output.

Existing real CLI wheel smoke and visual DOCX sample generation are retained.
Final source review, visual artifact review, four-environment CI and separately
authorized merge/exact post-merge evidence are required before closing #39.
