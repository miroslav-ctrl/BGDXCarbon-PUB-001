# SPR-015 Implementation Evidence

Status: implemented for review, 2026-10-19. No merge or final closure.
Baseline: develop c0b66f3ef7cbb58abc05b8d9155a9a62db29b071, approved plan PR #35.

## Change and boundaries

Only the batch CLI adapter changes production behavior. It resolves the registered
BatchHtmlPublicationService once, forwards BatchRequest unchanged, projects terminal
job states into document counts and safe ordinal/stage diagnostics, and buffers
stdout until runtime shutdown succeeds. Expected shutdown failure returns 1 without
stdout success claims. Publication diagnostics precede cleanup diagnostics; committed
files remain. Unexpected publication exceptions propagate; if unexpected shutdown
also fails, the primary exception remains active with a safe note.

Parser, legacy batch API, batch engine, single HTML, DOCX/PDF, runtime registration,
dependencies and version remain unchanged. CLI-facing tests move from legacy error
text to stable codes; direct legacy contract assertions are retained/extended.

## Acceptance mapping

New CLI tests: tests/cli/test_batch_cli_pipeline.py. The approved proposed filename
test_batch_pipeline.py collides with tests/batch_pipeline/test_batch_pipeline.py
under pytest's default import mode, so only the new test filename was adjusted.

| AC | Evidence prepared for review |
| --- | --- |
| 01 | Existing parser argument tests and test_parser_rejection_before_runtime; preflight mode of test_shutdown_and_primary |
| 02 | test_routing_and_equivalence spies on registered service and forbids legacy publish_batch/PublishingService publication |
| 03–04 | 16 differential theme/TOC/index/language combinations, UTF-8/BOM/Unicode source preservation, exact ordered stdout and BatchRequest |
| 05 | test_partial_and_empty_index_diagnostics; existing CLI continuation/index regression tests |
| 06 | Existing CLI preflight/index guards plus inherited batch service forbidden-publication preflight tests; no new transaction guarantee |
| 07 | Index race in test_shutdown_and_primary, retained competitor/document files; installed-wheel harness |
| 08 | Existing refusal/overwrite/race tests; test_postcommit_cleanup_and_primary_diagnostics retains failed-but-committed files and excludes them from index |
| 09 | Ten success/partial/preflight/index/unexpected × shutdown combinations, stream timing, primary-before-cleanup assertions; unexpected shutdown precedence tests; existing initialize/start/stop lifecycle tests |
| 10 | Captured safe ordinal/stage diagnostics and sentinel/path/content exclusion; existing inherited stage safe-log tests; runtime/config errors retain their separate existing boundary |
| 11 | Full suite, unchanged production direct API, explicit legacy preflight/alias/index/raw-diagnostic regressions |
| 12 | Local quality/coverage and isolated installed-wheel checks below; four-environment CI required before acceptance |

## Local results

Windows / Python 3.13.14, isolated development environment. Full suite:
**413 passed, 3 skipped**, total coverage **99.85%** (1945 statements, 3 missed).
CLI batch adapter: **100%** (50 statements). New CLI suite: **32 passed**.
Skips: batch case-sensitive filename collision and directory symlink privilege,
plus inherited HTML output symlink privilege. Linux CI must execute these cases.

Independent package gates (each --cov-fail-under=95):

| Package | Tests | Coverage |
| --- | --- | --- |
| domain | 17 passed | 100% |
| jobs | 20 passed | 100% |
| pipeline | 18 passed | 100% |
| orchestration | 14 passed | 100% |
| html_pipeline | 26 passed, 1 skipped | 100% |
| batch_pipeline | 24 passed, 2 skipped | 98.08% |

Ruff passes. Black checks 92 Python files. MyPy checks 57 source files without
issues. git diff --check passes. Tests/formatters ran outside sandbox after local
sandbox Python processes did not complete; results above are completed runs.

Wheel bgdxpublisher 1.1.0 built and installed with runtime dependencies in a fresh
venv. SHA-256: 06f521788f32e194ef96d7f6e49b62dba96ae4e220ce86207b285ff281226399.
The copied examples/batch_cli_pipeline.py ran outside checkout with isolated
Python (-I), empty PYTHONPATH, and an assertion that imports resolve to site-packages.
Exit 0 confirms complete success, refusal without overwrite, explicit overwrite,
partial/all-item failures, empty index, reserved-index preflight and independent
index failure retaining document/competitor bytes. No test-only runtime API added.
The workflow executes this same copied script in all four existing quality jobs.

CI, source review, separately authorized merge, exact post-merge CI and closure
remain required. Green existing/local tests do not establish final acceptance.
