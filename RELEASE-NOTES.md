# BGDXCarbon Publisher Suite 1.2.0 — 2026-10-22

Complete single and batch Markdown publishing through CLI and Python APIs.

## Included capabilities

Markdown-to-HTML, editable DOCX and selectable-text PDF, each with single and
batch command-line and Python pipeline APIs. Commands:

- publish / publish-batch (HTML), including existing light/dark styling,
  heading navigation and optional batch index.
- publish-docx / publish-docx-batch (DOCX).
- publish-pdf / publish-pdf-batch (PDF).

Registered pipelines share typed job orchestration, immutable terminal outcomes,
fresh contexts and safe stage-aware diagnostics. Existing direct legacy API
contracts remain available. Batch selection is immediate/nonrecursive and
stable; expected document failures continue with accurate counts. Each output
commits independently with explicit overwrite protection.

Success stdout is delayed until runtime shutdown succeeds. Failed postcommit
cleanup can leave a valid file while reporting failure; unexpected external
errors stop subsequent work and retain earlier commits. No whole-batch rollback.

## Installation and evidence

Python 3.13+; verified CI targets Windows/Linux and Python 3.13/3.14. Package,
runtime and both default configuration versions are 1.2.0.
GitHub assets: bgdxpublisher-1.2.0-py3-none-any.whl,
bgdxpublisher-1.2.0.tar.gz and SHA256SUMS.txt. Acceptance and publication
provenance are linked from the
[publication request](docs/releases/1.2.0/PUBLICATION-REQUEST.md).
No PyPI, installer or hosting publication is included.

## Limits

UTF-8 Markdown input; supported language-tag subset. DOCX/PDF images become alt
text; no binary-format templates, indexes/TOC or PDF/UA claim. PDF embeds bundled
licensed DejaVu fonts; unsupported glyphs fail explicitly (safe render-stage CLI
report; legacy direct API retains code-point diagnostics). Atomic no-overwrite
requires hard-link support; filesystem/symlink/alias policies are documented in
the usage guide. No recursive scan, parallel queue, rollback, GUI/cloud editor,
remote hosting, accounts or new distribution channel.

Published [1.1.0 notes](docs/releases/1.1.0.md) are preserved verbatim as history;
existing v1.0.0/v1.1.0 tags/assets are unchanged.
