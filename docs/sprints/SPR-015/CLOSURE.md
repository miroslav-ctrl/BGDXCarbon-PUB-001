# SPR-015 Closure Evidence

Date: 2026-10-19. Disposition: AC-01–AC-12 PASS; recommend formal closure.
Verified develop / PR #36 merge SHA: `a7ba8c41006d7b1e7cf7c2c37a4855f83cc6ffa8`.

## Implementation and review

[Plan PR #35](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/35) is merged and owner-approved.
[Implementation PR #36](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/36) is merged into develop.
Its reviewed head is 04a321474a47ca411db4eca8ba95ada37f62c973.
[Formal source review](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/36#pullrequestreview-5568538062)
concluded PASS without required corrections before merge. It is a Codex self-review
submitted as COMMENT, not an independent human APPROVE. The user supplied the GitHub
merge confirmation, and repository metadata independently confirms the merged SHA.
A separate prior merge-authorization record is not established by this evidence.

The implementation changes only production cli/batch.py plus scoped tests,
installed-wheel smoke/workflow invocation and documentation. Parser, legacy direct
batch API, engines, dependencies/version and unrelated command implementations
remain unchanged. Full criterion-to-test mapping is in IMPLEMENTATION-EVIDENCE.md.

## Exact post-merge CI

[Publisher CI 39220222386](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39220222386)
runs on the merge SHA above. All four quality jobs concluded success; decoded logs
were inspected. No local tests were rerun for this documentation-only closure.

| Environment | Job ID | Full suite | Total coverage | Batch package |
| --- | --- | --- | --- | --- |
| Ubuntu / Python 3.13 | 117953528457 | 416 passed | 99.90% | 26 passed / 100% |
| Ubuntu / Python 3.14 | 117953528289 | 416 passed | 99.89% | 26 passed / 100% |
| Windows / Python 3.13 | 117953528089 | 415 passed, 1 skipped | 99.90% | 25 passed, 1 skipped / 99.04% |
| Windows / Python 3.14 | 117953528550 | 415 passed, 1 skipped | 99.89% | 25 passed, 1 skipped / 98.99% |

The Windows skip is the case-sensitive filename collision case; Linux executes
all cases, including symlink protections. Domain/jobs/pipeline/orchestration/
html_pipeline each report 100% in every job. Total >=99% and all six independent
package >=95% gates pass. Ruff, Black, MyPy, wheel build and installed-wheel checks
succeed in all four jobs. The copied batch CLI smoke executes outside checkout and
checks installed site-packages imports, success/partial/all-failed outcomes,
overwrite, preflight and independent index failure.

## Acceptance conclusion

AC-01: unchanged parser; missing/invalid arguments exit 2, nonexistent-directory
preflight exits 1. AC-02: one registered batch service call, no legacy fallback.
AC-03–04: 16 differential combinations preserve output bytes, source bytes and
ordered success stdout. AC-05–08: partial/all failures, completed-only/empty index,
preflight guards, independent index failure, overwrite/race and postcommit cleanup
are covered. Committed files are retained; no rollback is promised.
AC-09–10: stdout is delayed until successful shutdown; failure returns 1, retains
primary diagnostics and files, and suppresses buffered success claims. Unexpected
exceptions propagate. Publication diagnostics use safe code/ordinal/stage, with
runtime/config diagnostics explicitly outside that replacement contract.
AC-11: unrelated commands/direct APIs have regression coverage.
AC-12: exact four-environment post-merge checks above pass.

## Administrative boundary

No separate SPR-015 implementation issue was found by repository issue search;
no issue was created or closed retroactively. This record completes the technical
post-merge acceptance evidence and proposes formal sprint closure through a
documentation PR to develop. It does not manufacture historical authorization or
independent review. No new implementation, branch deletion, release or main change.
The prior IMPLEMENTATION-EVIDENCE.md remains an accurate historical local report;
this document supersedes its pending-CI/review/merge disposition.
