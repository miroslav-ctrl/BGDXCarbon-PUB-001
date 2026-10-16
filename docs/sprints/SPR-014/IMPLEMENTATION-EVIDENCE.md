# SPR-014 Implementation Evidence

Baseline: develop 2f310d20529c97b93e99c0a75a96e1a3638efe71. Issue #31 remains open.
Status: implemented for review; merge and final acceptance closure pending.

New batch_pipeline composes HtmlPublicationService once per attempted source,
with immutable item/aggregate/index outcomes, safe preflight exceptions and
independent index commit. Runtime registers the service without CLI migration.
The legacy batch API and CLI remain unchanged.

## Acceptance mapping

Tests: tests/batch_pipeline/test_batch_pipeline.py.

| Criteria | Evidence |
| --- | --- |
| AC-01–03 | test_equivalence_and_invariants: eight theme/TOC/index cases, ordering, independent IDs, byte-equivalence and unchanged sources |
| AC-04 | test_preflight_before_publication: forbidden publication during invalid preflight |
| AC-05 | test_partial_and_empty_index: expected failure continuation and empty index |
| AC-06 | preflight alias/symlink tests and test_item_race_cleanup_and_single_attempts; inherited HTML protection tests |
| AC-07–08 | test_independent_index_and_postcommit_failures: index revalidation/alias failures, retained documents and failed-but-committed exclusion |
| AC-09 | single-attempt spies and safe captured logs |
| AC-10 | test_runtime_and_unexpected_dependency; examples/batch_pipeline.py installed-wheel success/partial/index failure checks |
| AC-11–12 | Full regression suite; independent batch_pipeline CI coverage gate |

## Local validation on 2026-10-16

Windows/Python 3.13.9: 380 passed, 3 skipped, aggregate coverage 99.79%.
Collection: existing 357 + new 26 = 383; 380 passed + 3 skipped = 383.
New package: 24 passed, 2 skipped, coverage 98.08% (102 covered of 104 statements).
New skips are case-sensitive filename collision and directory symlink privilege;
the existing HTML symlink test also skips locally. Linux CI must execute them.

Ruff passes; Black checks 89 Python files; MyPy checks 57 source files without
errors. Wheel builds and the copied batch example runs outside checkout against
the installed wheel with exit 0. Filesystem tests ran outside sandbox; portable
Python tests insert src explicitly while CI uses normal pytest configuration.

Document and index commits are independent. Postcommit cleanup failure retains a
file but reports FAILED and excludes it from index. No rollback is promised.
Review and exact successful post-merge CI remain required before issue #31 closure.
