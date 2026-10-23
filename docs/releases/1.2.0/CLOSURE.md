# Release 1.2.0 acceptance and closure

Status: publication acceptance COMPLETE. Recorded/revalidated 2026-10-23;
publication and downloaded-package execution completed 2026-10-22.
This document closes the accepted 1.2.0 scope, not deferred future product work.
Documentation integration is separate: this closure PR must pass its own CI and
owner-authorized merge; its exact merge/CI result belongs in the PR conversation.

## Published identity and authorization

- [Stable GitHub release v1.2.0](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/releases/tag/v1.2.0), ID 420617934, published 2026-10-22T11:06:27Z; draft=false, prerelease=false.
- Published source: `0747358001e88e399d141e132d0e8b38ec42f194`. Annotated tag object `d1cf4143d5a5598b22e0da557610e90378969193` resolves to this exact commit. Reviewed finalization head and merge have identical tree `b1e5918ea8440977e923a47675ea91e3b6f767ba`.
- Candidate accepted through [PR #70](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/70), publication request accepted through [PR #71](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/71), then owner separately authorized publication. [PR #72](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/72) finalized actual date/status before tagging.
- [Final publication execution record](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/72#issuecomment-6339325357) records the authorization, exact source, CI, assets and actual downloaded-package checks. Automated COMMENT reviews are disclosed self-review, not independent human APPROVE.
- Published release body exactly matched tagged RELEASE-NOTES.md. Distribution is GitHub only; no PyPI publication.

## CI evidence

| Stage | Exact source | Run | Result |
| --- | --- | --- | --- |
| Finalization PR head | ac706158d337a84f0820aec07df6010663f40000 | [39762894402](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39762894402) | SUCCESS |
| Final develop merge | 0747358001e88e399d141e132d0e8b38ec42f194 | [39766840118](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39766840118) | SUCCESS, attempt 1 |
| Tagged release | 0747358001e88e399d141e132d0e8b38ec42f194 | [39767474656](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39767474656) | SUCCESS, attempt 1; verification then publish |

Release jobs: Ubuntu/Python 3.13 `119786392962`, Ubuntu/Python 3.14 `119786392730`,
Windows/Python 3.13 `119786392354`, Windows/Python 3.14 `119786393020`;
publish `119788364083`. All succeeded. Ubuntu: 762 passed per environment;
Windows: 757 passed / 5 platform collision skips per environment. Total coverage 99.92%
on all four. Ten independent package >=95% gates pass: domain, jobs, pipeline,
orchestration, html_pipeline, batch_pipeline, docx_pipeline, pdf_pipeline,
docx_batch_pipeline, pdf_batch_pipeline. Windows batch_pipeline coverage is 99.04%
(Python 3.13)/98.99%(Python 3.14); other package gates 100%.

Ruff/Black/MyPy, builds, both fresh installed distributions and applicable sample
render/upload steps passed. The five Windows skips are case-collision filesystem
cases; hosted Linux executes those cases. They are not unverified feature failures.

## Public assets and independent verification

Exactly three public uploaded assets; current API identity/size/digests were
rechecked 2026-10-23 against retained actual downloads and the execution record.
These are release asset hashes, not hashes of earlier candidate builds.

| Asset | ID | Bytes | SHA256 |
| --- | --- | --- | --- |
| bgdxpublisher-1.2.0-py3-none-any.whl | 665594071 | 1665740 | f0f6906d01ea4f191f7a96e5edc9531129f2f02647969868a29a4e52f675d566 |
| bgdxpublisher-1.2.0.tar.gz | 665594068 | 1861237 | d4d2e73dd7342fcfea989d9a1d6a2de548e8ae93841e12f88ecb94fe87c40dbf |
| SHA256SUMS.txt | 665594072 | 196 | 2edffec57c4ab52860688d2d3764b63b8a21ace50d1c289c9805b54a52d5051b |

On 2026-10-22 all three assets were downloaded from public release URLs. Actual
bytes matched GitHub API digests, sizes and SHA256SUMS entries. A canonical export
of 279 tracked files used raw Git objects from the exact tagged source, avoiding
Windows checkout line-ending conversion. tools/verify_distributions.py passed:
version 1.2.0/metadata/dependencies, all 75 production modules/resources, both
configs, five fonts/license, documentation/examples/helpers and historical 1.1.0
notes. Regenerated checksum manifest was byte-identical to the public manifest.

Actual downloaded wheel AND sdist each passed the full CI installed verification
block in separate fresh venvs, with CLI/examples outside checkout and source
PYTHONPATH cleared. Sdist installation built its own wheel. Both completed exit 0:
version/doctor/config/runtime, direct and registered APIs, six single/batch
HTML/DOCX/PDF CLI commands, Unicode/metadata/OOXML/PDF semantic assertions,
HTML index/theme/navigation, overwrite/refusal/partial/preflight/read/glyph/
invalid-option/error/cleanup behavior. Host pypdf remained outside runtime dependencies.

Retained local evidence is supporting material; the linked PR execution record
is the durable remote record. Task-workspace output files:
release120-public-release.json, release120-public-verification.json,
release120-public-assets/, release120-public-installed-check.py and
release120-public-installed-check.log. Script SHA256:
`11e581a0d925c6b6da51fb6cea1a3867f578ade57335df764ac40de5165aab1f`;
completed log SHA256:
`7a64c81ab582029fe35cfe05a4eb2857232426e9de230dad73c487f550bf86b1`.
The log ends `PASS: downloaded wheel AND sdist full installed CLI/API/semantic/error/cleanup suite`.
This closure records the completed run; it does not claim a new installation run today.

## Acceptance disposition and limits

All RC-01 through RC-10 are satisfied; see [acceptance matrix](ACCEPTANCE.md).
The accepted edition covers local Markdown single/batch HTML, DOCX and PDF CLI/API
publication. Required feature tasks 55/59/63/67 were completed with sprint closure.
CLI/direct API compatibility and safe error/runtime cleanup contracts are retained.

Manual visual acceptance remains limited to the 20 pages in seven candidate
artifacts actually inspected under [candidate evidence](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/70#issuecomment-6336088396):
DOCX 1, PDF 1, PDF pipeline 6, batch DOCX API 2, batch DOCX CLI 2, batch PDF API 4,
batch PDF CLI 4. Release rendering/upload and semantic checks passed; no additional
manual inspection or universal rendering guarantee is claimed by this closure.

GUI, remote hosting/cloud, custom templates, embedded images, recursive processing,
queues, batch rollback and additional distribution channels remain outside 1.2.0.
Published 1.1.0 notes retain SHA256
`07bf7257f707d8db849ddefb0f5a10df586d4cb566308b2d10d91c29aa76067f`;
original candidate notes remain linked from CANDIDATE.md.

## Closure boundary

This PR changes documentation only on develop. It does not move v1.2.0, rebuild
or replace public assets, or republish the release. Published source remains
`0747358001e88e399d141e132d0e8b38ec42f194`; develop advances separately with
closure documentation. Main baseline remains
`9883eca15ef4642db6513efa4fa3610158312f27` and is excluded from all changes.
No branch deletion or history rewrite is included. Record this documentation PR's
review, exact head CI, merge SHA and post-merge CI in its conversation before
considering documentation integration complete.
