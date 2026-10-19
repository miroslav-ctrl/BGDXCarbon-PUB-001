# SPR-017 Acceptance and Closure Evidence

Verified 2026-10-19. Technical AC-01–AC-12 PASS on merged develop
`d39b2904d3189326d01e0b1313f6e6c6bff24382`. This documentation is submitted
for review; administrative closure is pending. Issue #43 remains open.

## Provenance and review

- Approved plan: [PR #42](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/42).
- Implementation baseline: `9e7cb64a97a1dff545c498afafa5f8527fb9a202`.
- Implementation: [PR #44](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/44), reviewed head `e30e2e0c83a92a656d39975bd0e8ad164de4c246`.
- [Formal review](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/44#pullrequestreview-5569465855): no blocking findings; disclosed Codex COMMENT, not independent human APPROVE.
- Owner explicitly accepted that review, authorized Ready for review, then separately authorized merge into develop in this task before merge.
- Implementation merge: `d39b2904d3189326d01e0b1313f6e6c6bff24382`.
- [Exact post-merge Publisher CI #105](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39231217588): push to develop, completed/success.

## Executed post-merge verification

Counts below come from completed job logs on the exact merge SHA, not planning
or earlier implementation runs. Python matrix versions are 3.13 and 3.14.

| Environment | Job ID | Full tests | Total coverage | Batch gate |
| --- | --- | --- | --- | --- |
| Ubuntu / 3.13 | 117989357805 | 469 passed | 99.90% | 100% |
| Ubuntu / 3.14 | 117989357918 | 469 passed | 99.90% | 100% |
| Windows / 3.13 | 117989357974 | 468 passed, 1 skipped | 99.90% | 99.04% |
| Windows / 3.14 | 117989357460 | 468 passed, 1 skipped | 99.90% | 98.99% |

All jobs succeed. Windows case-sensitive-filesystem batch collision case is
skipped; Linux runs the complete suite. Domain, jobs, pipeline, orchestration,
html_pipeline and docx_pipeline each independently reach 100% in all four jobs.
Batch independently passes >=95% as tabulated. Total >=99% is retained.

The committed `.github/workflows/ci.yml` executes Ruff, Black, MyPy, full pytest,
full coverage and seven separate package coverage commands. All pass, as do
wheel build and Test installed wheel outside repository. The latter creates a
fresh installation and exercises actual publish-docx success/Unicode/metadata,
refusal with previous bytes retained, overwrite, parser exit 2, safe missing
source validate failure and invalid UTF-8 read failure (exit 1/no traceback or
source path), alongside retained API smoke and other command regressions.
Exact reproducible commands remain in [VERIFY.md](VERIFY.md) and ci.yml.

Additional pre-merge review rerun: Windows/Python 3.13, `python -m pytest
tests/cli/test_docx_cli_pipeline.py tests/cli/test_docx_runtime_precedence.py
tests/publishing/test_docx.py tests/docx_pipeline/test_docx_publication.py -q
--basetemp=.pytest_cache/review-spr017`: 70 passed, 1 skipped (local DOCX symlink
privilege). These local counts are separate from hosted post-merge counts.

## Actual post-merge visual inspection

Downloaded [docx-preview artifact 12177485556](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39231217588/artifacts/12177485556)
from the exact merge run; archive SHA-256
`cf4a82291c29fd27905f1541880bb8e26c98f44bfddff5e59dcfecdbe17578db`.
Opened its `page-1.png`, the single page rendered from `sample.docx` through
LibreOffice/PDF/PNG by Ubuntu 3.13 after `bgdxpublisher publish-docx
examples/docx-sample.md --output docx-preview/sample.docx --lang sr-Latn`.
Serbian Latin/Cyrillic, headings, bold/italic/inline code, link, nested bullets,
numbered list starting at 3 and separate restart at 1, quote and code block are
readable with no visible clipping/overlap. This is actual inspection of that
sample, not a claim about every document or every Word installation.

## Accepted behavior and limits

See [AC mapping](ACCEPTANCE.md). Only cli/publish.py changed production behavior.
DOCX uses registered DocxPublicationService exactly once; parser/defaults and
PDF-first dispatch remain unchanged. Both direct APIs, renderer, writer,
registration and dependencies remain unchanged. Expected DOCX operational CLI
errors intentionally change to `Publication failed: DOCX_PUBLICATION_FAILED
stage=<stage>`, exit 1, with safe logs allowed; parser errors retain exit 2.
Runtime/config error formats remain outside the safe publication-message contract.

Expected shutdown failure emits cleanup diagnostic before the original primary
publication diagnostic; no duplicate primary and no success stdout. Unexpected
active DOCX primary survives unexpected shutdown with a safe note; unexpected
shutdown without primary propagates. Cleanup/shutdown failure after commit
retains the DOCX, with no rollback. Tests preserve unrelated command behavior.

## Administrative disposition

Technical implementation and exact post-merge acceptance are PASS. This closure
record supersedes pending source-review/CI/visual/post-merge statements in
historical IMPLEMENTATION-EVIDENCE.md; it does not rewrite those executed results.
Closure-document review, owner acceptance, separately authorized documentation
merge and its exact post-merge CI must precede completing
[issue #43](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/43).
This submission performs none of those later actions. No release or branch
deletion; main unchanged at `9883eca15ef4642db6513efa4fa3610158312f27`.
