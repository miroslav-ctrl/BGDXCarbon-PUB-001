# SPR-012 Implementation Evidence

Baseline: develop f62cf552fcb54967b1f3c16d5000c33cabdfe590. Issue #25 is closed as completed.
Status: merged and formally closed; see [closure evidence](CLOSURE.md).

New bgdxpublisher.html_pipeline composes validate/read/render/write stages with
JobExecutionService. Frozen payloads carry validated options, decoded Markdown and
rendered HTML. Existing renderer, output policy and atomic writer are reused.
Runtime registers HtmlPublicationService without replacing the empty default
coordinator or changing CLI routes. examples/html_pipeline.py demonstrates real
publication, legacy byte-equivalence and typed failure handling.

## Acceptance mapping

| Criteria | tests/html_pipeline/test_publication.py evidence |
| --- | --- |
| AC-01–04 | test_equivalence: eight metadata/theme/TOC combinations; source preservation, exact output bytes/count, order, lifecycle and frozen result |
| AC-05 | test_invalid_metadata_preserves_files, test_stage_failure_chain_and_safe_logs, test_encoding_failure |
| AC-06 | test_invalid_paths, test_output_symlink, test_no_overwrite_race_and_cleanup |
| AC-07 | test_precommit_write_failure_and_cleanup, test_postcommit_cleanup_and_context_isolation |
| AC-08–09 | test_runtime_and_single_operations, context isolation and captured-log sentinel checks |
| AC-10 | Runtime test and examples/html_pipeline.py copied outside checkout; CI executes it with installed wheel |
| AC-11–12 | Full regression suite; independent adapter coverage gate added to four-platform CI |

The atomic commit boundary has no automatic rollback. A cleanup failure after
successful commit reports FAILED with no output result while the committed file
remains. Precommit failures and no-overwrite races preserve existing output;
temporary files are cleaned by the shared writer. See IMPLEMENTATION-SPEC.md.

## Local validation on 2026-10-16

Windows / Python 3.13.9: 341 passed, 1 skipped, total coverage 99.89%.
Dedicated adapter tests: 26 passed, 1 skipped, 100% package coverage. The skipped
test requires Windows symlink privilege; Linux CI must execute that case.
Ruff passes; Black check passes (84 Python files); MyPy passes (55 source files).
Wheel built and installed in the isolated local runtime; copied HTML pipeline
example executed outside checkout with exit 0. Filesystem tests ran outside the
restricted sandbox. The portable Python test invocation explicitly inserts src;
standard CI uses project pytest configuration.

PR review and exact post-merge CI verification are complete. AC-01–AC-12 passed;
see CLOSURE.md for final evidence and issue #25 closure.
