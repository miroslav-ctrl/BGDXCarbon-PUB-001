# Request to publish BGDXCarbon Publisher Suite 1.2.0

Status: Draft request only, 2026-10-22. Publication NOT authorized or executed.
Opening/reviewing/merging this request is not permission to push a tag or publish.
No main change is proposed. Current published release remains v1.1.0.

## Proposed publication

Publish stable GitHub release/tag v1.2.0 for the approved 1.2.0 CLI/API edition.
Distribution stays GitHub only: no PyPI, installer or new channel. Expected assets:

- bgdxpublisher-1.2.0-py3-none-any.whl
- bgdxpublisher-1.2.0.tar.gz
- SHA256SUMS.txt covering those two archives

Root RELEASE-NOTES.md is the staged publication text consumed by the existing
release workflow. The candidate wording is preserved in
[immutable candidate notes](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/blob/91f63e981feacd23bdff288e1064944386ebed56/RELEASE-NOTES.md); published1.1.0 notes remain
unchanged in [history](../1.1.0.md). Candidate-notes Git SHA256:
`fbe9942714dd63ed723558d8a9214589a81d2e28983eaed92c214aaff30b27b0`. The request does not assert that 1.2.0 has
already shipped. Current README/changelog retain unpublished-candidate status.

## Accepted candidate and integration proof

- Candidate [PR #70](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/70) reviewed without blocking findings; [review5611300280](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/70#pullrequestreview-5611300280).
- Owner explicitly requested the formal review and merge in this task. Candidate merged into develop at `91f63e981feacd23bdff288e1064944386ebed56`.
- [Exact post-merge CI39747742484](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39747742484), attempt2, SUCCESS on all four Ubuntu/Windows Python3.13/3.14 environments. Ubuntu762passed; Windows757passed/5collision skips; total99.92%; all10independent>=95% gates pass.
- First Ubuntu3.13 attempt timed out while downloading LibreOffice from the Ubuntu mirror. Only that job was repeated, unchanged source, and succeeded. [Final integration record](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/70#issuecomment-6337382067) preserves both attempts.
- Complete wheel AND sdist fresh-install actual CLI/API/semantic checks,75packaged production files/configs/five fonts/license and checksums pass. [Candidate evidence](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/70#issuecomment-6336088396) records all20actually inspected pages in seven visual artifacts, exact digests and package verification.
- Reviewed head/accepted merge have identical tree `ac4fbab303a0322afc68b82ce85b76b9fef99bc3`. This request changes documentation/release text only, preserving package identity1.2.0 and implementation behavior; its own exact-head CI is separate proof.
- Required feature issues55/59/63/67 are completed. The accepted scope remains HTML/DOCX/PDF single and batch CLI/APIs; deferred GUI/cloud/templates/images/queues/rollback work is not added.

## Proposed execution after separate authorization

1. Review this request and its final-head CI; obtain owner acceptance and a
   separate merge instruction. Verify exact request merge SHA/CI before using it.
2. Obtain explicit authorization to publish v1.2.0. Recheck that tag/release are
   unused, source version/configs agree and no blocking findings remain. Do not
   use an old candidate SHA if release text/status changed afterward.
3. Under that publication authorization, finalize the actual release date and
   README/changelog publication status; verify the resulting exact source/CI.
   Record the approved final source SHA. These date/status edits must precede
   tag creation; do not invent a publication date in this Draft request.
4. Tag only the approved final develop commit as v1.2.0 and push that tag. This
   triggers .github/workflows/release.yml: verify reuses the full CI matrix;
   publish runs only after verify succeeds and tag version equals package version.
   Root RELEASE-NOTES.md supplies the staged text. Build fresh wheel/sdist and
   SHA256SUMS; do not substitute candidate CI build hashes for release asset hashes.
5. Verify the resulting GitHub release URL/tag/target commit, stable publication
   state, exact three assets, sizes and SHA256SUMS. Download both release archives
   and independently verify checksums and packaged version/config/fonts/license.
6. Run fresh downloaded wheel AND source-archive installs outside checkout with
   source PYTHONPATH cleared: version/doctor and retained actual single/batch
   HTML/DOCX/PDF CLI/API smoke, semantic/metadata/error/cleanup checks. Record
   exact source/run/asset digests and results before declaring publication complete.

If verification fails, stop publication/acceptance progression and report the
actual state. Do not silently retag or replace previously published assets. Any
replacement/version decision requires explicit owner direction. Main remains
outside the publication path; no branch deletion is part of this request.

## Approval and execution checklist

- [x] Candidate formally reviewed, owner-authorized merge and exact merge CI PASS.
- [x] All required feature sprints completed; scope unchanged.
- [x] Staged release text and preserved candidate/published notes prepared.
- [ ] Exact request-head CI and final request review accepted by owner.
- [ ] Separately authorized request merge and exact post-merge CI.
- [ ] Explicit authorization to publish v1.2.0 and approved final source SHA.
- [ ] Actual date/status finalized and verified before tag creation.
- [ ] Tag/release workflow, three public assets and checksums verified.
- [ ] Downloaded wheel/sdist fresh-install acceptance and final release evidence.

Public release authorization: PENDING. Tag: NOT created. GitHub release: NOT
created. Main remains `9883eca15ef4642db6513efa4fa3610158312f27`.
