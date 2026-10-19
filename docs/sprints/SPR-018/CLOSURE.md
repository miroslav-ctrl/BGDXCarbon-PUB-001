# SPR-018 Acceptance and Closure Evidence

Verified 2026-10-19. Technical AC-01–AC-12 PASS on merged develop
`e5505be5b3f3e12a2bceebbb471ca79ddca14c19`. Closure documentation submitted
for review; administrative closure pending. Issue #47 remains open.

## Provenance and review

- Approved plan: [PR #46](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/46); implementation baseline `97e57f643c4a05f0244a65363850d8f18eb6cdaf`.
- Implementation: [PR #48](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/48), reviewed head `4196a9fcb0232a788c99a2a29d7d6c16cbc07fc8`.
- [Formal implementation review](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/pull/48#pullrequestreview-5570766325): no blocking findings; Codex COMMENT, not independent human APPROVE.
- Owner accepted the review, authorized Ready for review, then separately authorized implementation merge in this task before merge.
- Merge into develop: `e5505be5b3f3e12a2bceebbb471ca79ddca14c19`.
- [Exact post-merge Publisher CI 39244005897](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39244005897): push on the merge SHA, completed/success.

## Executed exact-merge CI

| Environment | Job ID | Full tests | Total coverage | Batch coverage |
| --- | --- | --- | --- | --- |
| Ubuntu / Python 3.13 | 118031376363 | 511 passed | 99.91% | 100% |
| Ubuntu / Python 3.14 | 118031376175 | 511 passed | 99.90% | 100% |
| Windows / Python 3.13 | 118031376333 | 510 passed, 1 skipped | 99.91% | 99.04% |
| Windows / Python 3.14 | 118031376848 | 510 passed, 1 skipped | 99.90% | 98.99% |

Windows skips the case-sensitive batch collision test; Linux executes all tests.
Eight independent >=95% package gates pass in every job. Domain, jobs, pipeline,
orchestration, html_pipeline, docx_pipeline and new pdf_pipeline reach 100%;
batch is tabulated above. Total >=99% retained. Ruff/Black/MyPy, wheel build,
fresh installed-wheel checks and configured visual generation/upload all pass.

Executed commands are the committed `.github/workflows/ci.yml` steps: `python -m
ruff check .`, `python -m black --check .`, `python -m mypy src`, `python -m pytest`,
full coverage with --cov-fail-under=99 and eight separate package commands with
--cov-fail-under=95, including `python -m pytest tests/pdf_pipeline
--cov=bgdxpublisher.pdf_pipeline --cov-report=term-missing --cov-fail-under=95`.
See [VERIFY.md](VERIFY.md) for reproducible commands. Counts here are completed
hosted post-merge results, separate from historical local evidence.

Fresh wheel API check copies examples/pdf_pipeline.py outside checkout, removes
source PYTHONPATH and runs with isolated Python (-I); example asserts installed
site-packages imports, COMPLETED result/bytes, fresh jobs, refusal/overwrite and
safe encoding failure with retained output. Host pypdf verifies title/language,
Unicode and single/multipage output. Existing actual PDF CLI and other API/CLI
smoke checks remain and pass. pypdf remains development-only; no dependency or
version change. Runtime lifecycle remains caller-owned.

## Actual exact-merge visual inspection

Downloaded [pdf-pipeline-preview artifact 12182004931](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39244005897/artifacts/12182004931)
from the exact merge run. Downloaded ZIP SHA-256 matches artifact digest:
`3ed483d38cc50c294153daa52679501374ef78a9ce90720460da9973ea6246ff`.
Opened every generated PNG: sample-page-1.png and multipage-page-1.png through
multipage-page-5.png (six pages total). These are new PdfPublicationService API
outputs, distinct from retained legacy CLI pdf-preview and docx-preview artifacts.

Ubuntu 3.13 executes `python -I examples/pdf_pipeline.py pdf-pipeline-preview
examples/pdf-sample.md`, then pdftoppm at 100 dpi for sample.pdf and multipage.pdf.
The shipped single-page sample shows readable Latin/Cyrillic, headings,
bold/italic/inline code, link, nested bullets, numbering from 3 and restart at 1,
quote and code. Five-page fixture shows paragraphs over pages 1–3 and Cyrillic
code continuing over pages 4–5. No visible clipping/overlap or broken pagination.
This claim covers these six pages, not every possible input/viewer.

## Accepted behavior and limits

[ACCEPTANCE.md](ACCEPTANCE.md) maps all criteria to tests and review evidence.
New typed PDF API uses validate/read/render/write, fresh jobs/contexts, consistent
immutable result and fixed PDF_PUBLICATION_FAILED string/code with structured
stage and inspectable internal causes. Safe new-route logs exclude raw user data.
Font/layout/glyph/control failures are render stage. CLI and legacy direct API
keep their original diagnostics/route, including raw legacy details.

Registered engine cleanup failure after commit yields FAILED/stage=cleanup with
no successful output envelope while retaining committed PDF; cleanup once per
independent context, no rollback. Internal shared-writer exceptions remain write
stage under existing engine semantics. Caller owns initialize/start/finally-stop;
no CLI shutdown or PDF-first precedence changes. Existing renderer/fonts/writer,
engine/orchestration, parser, legacy direct API and old tests remain unchanged.

## Administrative disposition

Technical implementation and exact post-merge acceptance PASS. This closure record
supersedes pending review/CI/visual/post-merge dispositions in historical
IMPLEMENTATION-EVIDENCE.md without rewriting local executed results. Additional
formal-review rerun was 73 passed/1 local symlink skip on Windows/Python 3.13;
that is not a hosted post-merge count.

Closure-document formal review, owner acceptance, separately authorized merge
and its exact post-merge CI must precede completing
[issue #47](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/47).
This submission leaves issue open and does not perform those future steps.
No release/tag or branch deletion; main unchanged at
`9883eca15ef4642db6513efa4fa3610158312f27`.
