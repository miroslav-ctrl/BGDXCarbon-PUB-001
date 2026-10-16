# SPR-013 Implementation Evidence

Baseline: develop a3f739c815a08cb3cd37d12ae1cd733a66222bd6. Issue #28 remains open.
Status: implemented for review; merge and final acceptance closure pending.

HTML run_publish resolves HtmlPublicationService and adapts its publication result.
HtmlPublicationError is handled explicitly using structured failure stage and code;
causes are never stringified. Primary failure survives a simultaneous shutdown
failure. Existing PDF/DOCX branches and batch/direct legacy APIs remain unchanged.

## Acceptance mapping

| Criteria | Evidence |
| --- | --- |
| AC-01–03 | tests/cli/test_html_pipeline.py::test_html_routing_and_equivalence: eight combinations, forbidden legacy call, captured request, exact stdout, byte-equivalence and source preservation |
| AC-04–05 | test_parser_failure_never_initializes_runtime and test_safe_stage_errors; existing parser/missing-source tests |
| AC-06–07 | test_shutdown_failure_preserves_primary, test_postcommit_cleanup_failure_retains_output; existing lifecycle and filesystem regressions |
| AC-08 | Full CLI/publishing regression suite |
| AC-09 | Extended installed-wheel CI assertions for refusal/missing-source safe diagnostics; existing success/overwrite/metadata checks retained |
| AC-10 | Local quality/coverage below; four-platform CI remains required |

## Local validation on 2026-10-16

Windows/Python 3.13.9: 356 passed, 1 skipped (symlink privilege), aggregate coverage
99.89%. The suite adds 15 cases to the existing 342-case collection: 342 + 15 = 357;
356 executed successfully and 1 was skipped locally. Ruff passes; Black checks 85
Python files; MyPy checks 55 source files without errors.

Wheel built and installed in the isolated runtime. Outside checkout, python -m
bgdxpublisher publish checks pass for success, refusal without overwrite and
invalid-language parser exit 2. CI repeats wheel checks in fresh environments.

Safe pipeline logs can appear on stderr alongside the single primary Publication
failed line. Tests assert that raw exception text and source paths from causes do
not appear. The user guide documents the intentional diagnostic change and the
postcommit no-rollback boundary.

Filesystem tests and formatter workers ran outside the restricted sandbox. The
portable interpreter uses explicit src insertion for tests; CI uses normal pytest
configuration. No acceptance closure is asserted before review and post-merge CI.
