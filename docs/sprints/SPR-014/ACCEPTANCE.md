# SPR-014 Acceptance Criteria

Status: post-merge acceptance verified on 2026-10-19 against `c9c47db2f34cbf6ea186a5d2695b107976cba8a1`.
[PR #33](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/33) is merged into develop; [issue #31](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/31) is closed/completed.
This record reconciles the former planning checklist with the merged implementation and existing CI. No local tests were rerun for this documentation update.

## Acceptance results

Test names below refer to [tests/batch_pipeline/test_batch_pipeline.py](../../../tests/batch_pipeline/test_batch_pipeline.py), unless another path is given.
Implementation: [batch service](../../../src/bgdxpublisher/batch_pipeline/service.py).

| ID | Criterion | Result and evidence |
| --- | --- | --- |
| AC-01 | Legacy nonrecursive discovery, case-insensitive .md selection and ordering | PASS: test_equivalence_and_invariants selects A.md and b.MD, excludes nested Markdown and ignore.txt, and asserts deterministic order. |
| AC-02 | Independent jobs/contexts per attempted item | PASS: test_equivalence_and_invariants asserts distinct job IDs; test_independent_index_and_postcommit_failures captures distinct contexts. Inherited test_postcommit_cleanup_and_context_isolation in tests/html_pipeline/test_publication.py also checks repeated calls. |
| AC-03 | Byte-equivalent HTML for identical inputs/options | PASS: eight theme/TOC/index combinations in test_equivalence_and_invariants compare document/index bytes with legacy publish_batch and preserve UTF-8/BOM sources. Inherited HTML test_equivalence also covers default/custom title and language. |
| AC-04 | Stem collisions and index.md conflict rejected before publication | PASS: test_preflight_before_publication includes collision and index cases with a forbidden publication spy; all 26 batch cases execute on Linux. |
| AC-05 | Expected item failure does not stop remaining items | PASS: test_partial_and_empty_index covers mixed invalid/valid UTF-8 and all-failed inputs, typed FAILED result, no pipeline output, and completed-only or empty index. |
| AC-06 | Source/overwrite/alias/symlink/race protections retained | PASS: preflight index alias/overwrite checks, test_output_directory_symlink and test_item_race_cleanup_and_single_attempts; inherited HTML test_invalid_paths, test_output_symlink, test_no_overwrite_race_and_cleanup and test_precommit_write_failure_and_cleanup. |
| AC-07 | Index includes completed items only; independent index failure preserves documents | PASS: test_partial_and_empty_index and race/alias cases of test_independent_index_and_postcommit_failures assert outcomes and retained files. Byte comparison reuses legacy index rendering; shared escaping/security regressions remain in the full suite. |
| AC-08 | Postcommit cleanup failure is FAILED and excluded from index without rollback | PASS: cleanup case of test_independent_index_and_postcommit_failures retains files, marks jobs FAILED and excludes the failed item from index. No rollback is claimed. |
| AC-09 | Safe logs and exactly one publication attempt per item | PASS: test_item_race_cleanup_and_single_attempts asserts one destination commit attempt per item; batch service calls publisher once per loop iteration. Captured batch logs exclude source paths/raw sentinel exception; inherited test_stage_failure_chain_and_safe_logs excludes document content. |
| AC-10 | Runtime and installed wheel support success/partial/index failure | PASS: test_runtime_and_unexpected_dependency resolves the service and preserves unexpected exception propagation; examples/batch_pipeline.py verifies success, partial failure and independent index failure against the installed wheel outside checkout in all four CI jobs. Empty successful index is covered by test_partial_and_empty_index. |
| AC-11 | Existing CLI and direct APIs unchanged | PASS: PR #33 does not change CLI or legacy publishing implementation; differential tests and full suite pass. Installed-wheel step also runs existing CLI smoke checks. |
| AC-12 | Quality and coverage pass in four environments | PASS: exact post-merge run below; Ruff, Black, MyPy, tests, total >=99%, all six independent package gates >=95%, wheel build and installed-wheel checks succeed in every job. |

## Exact post-merge CI evidence

[Publisher CI run 38888501872](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/38888501872), executed 2026-10-16 on the merge SHA above, concluded success. Decoded logs and step conclusions were inspected on 2026-10-19.

| Environment | Job | Full suite | Total coverage | Batch suite | Batch coverage |
| --- | --- | --- | --- | --- | --- |
| Ubuntu / Python 3.13.16 | [116932009867](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/38888501872/job/116932009867) | 383 passed | 99.90% | 26 passed | 100.00% |
| Ubuntu / Python 3.14.8 | [116932010194](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/38888501872/job/116932010194) | 383 passed | 99.89% | 26 passed | 100.00% |
| Windows / Python 3.13.16 | [116932010158](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/38888501872/job/116932010158) | 382 passed, 1 skipped | 99.84% | 25 passed, 1 skipped | 99.04% |
| Windows / Python 3.14.8 | [116932010185](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/38888501872/job/116932010185) | 382 passed, 1 skipped | 99.84% | 25 passed, 1 skipped | 98.99% |

The Windows batch skip is the collision case requiring a case-sensitive filesystem (the 14th collected case); Linux executes it. The symlink cases execute in these hosted CI jobs. Earlier local skips in IMPLEMENTATION-EVIDENCE.md describe a different environment and are historical.

Commands in [.github/workflows/ci.yml](../../../.github/workflows/ci.yml): `python -m ruff check .`, `python -m black --check .`, `python -m mypy src`, `python -m pytest`, total coverage with `--cov=bgdxpublisher --cov-fail-under=99`, and six independent package coverage commands with `--cov-fail-under=95` for domain, jobs, pipeline, orchestration, html_pipeline and batch_pipeline. Each uses `--cov-report=term-missing`; targeted runs use their matching tests directory. Domain/jobs/pipeline/orchestration/html_pipeline report 100% in every job. The wheel step builds with `python -m pip wheel . --no-deps --wheel-dir dist-review` and executes the copied batch example in a fresh environment outside checkout.

## Review and historical limits

This is a retrospective source/test/CI review. GitHub returns no submitted reviews for PR #33. Its merged state confirms the merge occurred, but does not independently establish the prior review/authorization record or that evidence was recorded before issue closure. That historical checklist item remains unconfirmed; this update does not manufacture it. Functional acceptance AC-01 through AC-12 is supported by the evidence above.

This PR changes documentation only, targets develop, and performs no merge or main update. IMPLEMENTATION-EVIDENCE.md, SPR-014.md and VERIFY.md retain their original pre-merge narrative; the current acceptance disposition is recorded here.
