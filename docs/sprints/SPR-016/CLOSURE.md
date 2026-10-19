# SPR-016 Closure Evidence

Date: 2026-10-19. Technical disposition: AC-01–AC-12 PASS.
This documentation PR proposes formal closure; issue #39 remains open until the
closure record is accepted. No issue closure or new merge is performed here.

## Baseline, authorization and source review

[Approved plan PR #38](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/38) preceded implementation.
[Implementation PR #40](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/40) merged into develop as
`c98be074d96d1bc95affa86718a91e58f52bb8a1`. Reviewed head:
353423ce435d0cf983435fec5597e5f23ed4f7cb.

The owner explicitly requested formal review and merge to develop before the
operation. [Review 5569054446](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/40#pullrequestreview-5569054446)
recorded PASS before merge. This is disclosed Codex self-review as COMMENT, not an
independent human APPROVE. The review records the explicit authorization.
Implementation issue: [#39](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/39).

## Exact post-merge CI

[Publisher CI 39225799217](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39225799217)
ran on the exact merge SHA above and concluded success. Step outcomes and decoded
logs were inspected; no local test rerun was needed for documentation-only work.

| Environment | Job ID | Full suite | Total coverage | DOCX suite / coverage |
| --- | --- | --- | --- | --- |
| Ubuntu / Python 3.13 | 117971656827 | 447 passed | 99.90% | 31 passed / 100% |
| Ubuntu / Python 3.14 | 117971656721 | 447 passed | 99.90% | 31 passed / 100% |
| Windows / Python 3.13 | 117971656412 | 446 passed, 1 skipped | 99.90% | 31 passed / 100% |
| Windows / Python 3.14 | 117971656682 | 446 passed, 1 skipped | 99.90% | 31 passed / 100% |

Windows skips only the pre-existing case-sensitive batch filename collision case.
All DOCX cases execute in hosted Windows and Linux; Linux executes all 447 cases.
Seven independent >=95% gates pass. Domain/jobs/pipeline/orchestration/html_pipeline/
docx_pipeline are 100% in every job; batch_pipeline is 100% on Linux and
99.04%/98.99% on Windows 3.13/3.14. Total >=99% passes.
Ruff, Black, MyPy, wheel build and installed-wheel checks succeed throughout.
The copied API example checks installed imports outside checkout, runtime service
selection, Unicode/metadata, OOXML member equality, overwrite/failure preservation
and independent jobs. Existing real DOCX CLI smoke remains successful.

## Visual evidence and its scope

[Pre-merge CI 39225071063](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39225071063)
also succeeded on the reviewed head. Its
[docx-preview artifact 12172939610](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39225071063/artifacts/12172939610),
from Ubuntu/Python 3.13 job 117969238601, contains sample.docx, sample.pdf and
page-1.png. The single page was actually opened and inspected on 2026-10-19,
as [recorded on PR #40](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/40#issuecomment-6263357137).

Observed: readable Serbian Latin/Cyrillic, headings, bold/italic/inline code, link,
nested bullets, numbering 3/4 and separate 1/2, quote and code block; no clipping,
overlap or missing glyphs. This is the retained legacy CLI visual sample, not a
claim that CLI routing migrated. The new API reuses the unchanged DocxRenderer;
differential tests compare all uncompressed OOXML members without XML normalization.
The combined visual and structural evidence supports retained layout/content.
No separate post-merge image inspection is claimed.

## Acceptance and compatibility

All twelve criteria are mapped in ACCEPTANCE.md and IMPLEMENTATION-EVIDENCE.md.
New service: typed validate/read/render/write, immutable snapshots/results, full
internal cause chains and fixed safe logs. Source/alias/symlink/overwrite/race and
shared permission guards remain; precommit failure preserves existing bytes,
postcommit cleanup may retain a file while reporting FAILED, without rollback.
Independent jobs/contexts and one read/render/write are verified.

CLI, direct DocxPublishingService API, legacy renderer, dependency/version and other
routes are unchanged. The new API is separately registered and optional.
Local Windows results in IMPLEMENTATION-EVIDENCE.md describe a distinct environment
(443 passed, 4 skipped / 99.85%) and are not substituted for hosted CI evidence.

## Closure recommendation

Technical acceptance is PASS, with no unresolved implementation defect identified
in formal review. Accept this closure record, merge documentation only after
separate authorization, verify that merge CI, then close #39 as completed.
main remains unchanged at 9883eca15ef4642db6513efa4fa3610158312f27.
No release, feature-branch deletion or additional implementation is included.
