# Release 1.2.0 Candidate

Status: unpublished candidate prepared for Draft review, 2026-10-22.
Owner acceptance of the exact candidate, merge and publication remain separate
future authorizations. No tag/release/main change is performed by preparation.

## Baseline and identity

Current develop baseline: `18ece520694fdb722ec4134b7aea4c557aeceef2`, after
SPR-023 closure [PR #69](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/69).
[Baseline CI39743153859](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39743153859)
is SUCCESS across Windows/Linux Python 3.13/3.14. Baseline is implementation proof,
not a substitute for candidate-head CI after version/package/doc changes.
Main remains `9883eca15ef4642db6513efa4fa3610158312f27`.

At preparation time GitHub has published v1.0.0/v1.1.0 only; no v1.2.0 tag or
release exists. Recheck availability immediately before authorized publication.
Package target is 1.2.0 (not a published rc tag); Draft status and exact commit
identify the candidate. Versions agree in pyproject.toml, src/bgdxpublisher/version.py,
configs/default.yaml and src/bgdxpublisher/config/default.yaml. Current default
CLI assertions/CI metadata checks and installed examples use1.2.0. Custom-config
regression fixtures intentionally retain arbitrary older/override versions.
Runtime dependencies/platform requirements are unchanged; build is a CI tool.

## Accepted capability matrix

| Format | Single CLI | Batch CLI | Single / batch pipeline API |
| --- | --- | --- | --- |
| HTML | publish | publish-batch | Preserved |
| DOCX | publish-docx | publish-docx-batch | Available |
| PDF | publish-pdf | publish-pdf-batch | Available |

The [accepted scope](../../FIRST-COMPLETE-RELEASE-SCOPE.md) is unchanged. Completed
pipeline/CLI migrations remain in sprint records; latest required feature closures:

| Work | Accepted evidence | Completed tracking issue |
| --- | --- | --- |
| SPR-020 DOCX batch API | [closure](../../sprints/SPR-020/CLOSURE.md), PR #57 | [#55](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/55) |
| SPR-021 DOCX batch CLI | [closure](../../sprints/SPR-021/CLOSURE.md), PR #61 | [#59](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/59) |
| SPR-022 PDF batch API | [closure](../../sprints/SPR-022/CLOSURE.md), PR #65 | [#63](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/63) |
| SPR-023 PDF batch CLI | [closure](../../sprints/SPR-023/CLOSURE.md), PR #69 | [#67](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/67) |

Sprint closure documents retain submission-time pending text; final merged PR
verification/issue completion entries record later authorized closure. All four
issues above must be verified completed for candidate acceptance.

## Packaging and history

Expected build outputs: bgdxpublisher-1.2.0-py3-none-any.whl,
bgdxpublisher-1.2.0.tar.gz and SHA256SUMS.txt. python -m build builds source archive
then wheel from that archive. tools/verify_distributions.py checks archive metadata,
all production modules/resources against checkout bytes, both configs, all five
DejaVu fonts and their license, source examples/tools/release docs, then writes
checksums of the two archives. Both fresh wheel and source-archive installs run
all existing actual command/API/semantic smoke outside checkout with source
PYTHONPATH removed. No runtime pypdf dependency is added.

MANIFEST includes executable examples and verification tooling so source-archive
verification/tests can find their helpers. Dependencies and renderer/fonts/writer/
engine/lifecycle behavior are unchanged; only package identity and evidence
infrastructure are prepared. Archive hashes can vary between builds; use the
exact run/artifact and its own SHA256SUMS, not a different local build's hash.

Published 1.1.0 notes are preserved verbatim in [history](../1.1.0.md), SHA256
`07bf7257f707d8db849ddefb0f5a10df586d4cb566308b2d10d91c29aa76067f`.
Root RELEASE-NOTES.md now describes only the unpublished 1.2.0 candidate and links
to that history. Published changelog 1.1.0/1.0.0 sections and old GitHub assets/tags
are unchanged. Existing font files/license are unchanged and checked in packages.

## Required candidate proof and boundary

See [acceptance checklist](ACCEPTANCE.md) and [verification](VERIFY.md). Record
exact candidate head/PR/run/jobs, dependency versions, counts/skips, both-install
results, artifact checksums and actual visual inspection scope in the candidate
PR evidence. This source record cannot embed its own future commit/archive digest.
Local results must be distinguished from exact-head hosted proof. Any repaired
candidate needs updated final-head CI/evidence before acceptance.

Required preview scope: retained single DOCX/PDF, PDF pipeline single/multipage,
DOCX batch API/CLI and PDF batch API/CLI samples; open ALL PNG pages in each
candidate acceptance artifact. Upload/generation alone is not manual inspection.
HTML output/index/theme/navigation and all formats' semantics are exercised in
the installed CLI/API suite. No blanket manual claim for all possible documents.

No known implementation blocker is carried from accepted SPR-023; candidate
verification is still required. Owner acceptance of the exact head is PENDING.
After review/acceptance, merge requires separate authorization and exact merge
CI; tag/release/assets publication and downloaded-asset verification require
another explicit authorization. Do not declare 1.2.0 published or edition complete
until those conditions are satisfied. GUI/cloud/hosting/templates/embedded images/
recursive processing/queues/rollback/new distribution channels remain deferred.
