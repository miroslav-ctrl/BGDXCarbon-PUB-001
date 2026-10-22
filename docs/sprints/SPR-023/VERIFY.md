# SPR-023 Verification Plan

Proposed implementation checks, not baseline proof of future behavior:

- python -m ruff check .; python -m black --check .; python -m mypy src
- python -m pytest tests/cli/test_pdf_batch_cli_pipeline.py tests/cli/test_pdf_batch_runtime_precedence.py
- Full pytest and --cov=bgdxpublisher --cov-fail-under=99; retain all ten
  independent package>=95% gates, including pdf_batch_pipeline.
- Parser/dispatch/exact request, real mixed/all/read/glyph/render/write/cleanup,
  all expected preflight and both-overwrite symlink policies; sentinel INFO logs.
- Body success/mixed/all/preflight/runtime/unexpected crossed with stop success/
  expected/unexpected, startup states/constructor/real unexpected earlier commit.
- Fresh installed wheel outside checkout; copy runtime-only PDF batch CLI example,
  clear source PYTHONPATH, use -I and installed-import assertion. Execute actual
  command/config/help/rejections/statuses/overwrite and injected shutdown checks.
- Host/dev pypdf compares CLI and direct batch results under SPR-022 semantic
  rules; no new runtime dependency. Retain all prior installed CLI/API checks.
- Actual new CLI sample and multipage PDFs; rasterize/open ALL pages and record
  commit/run/jobs/artifact/ZIP digest/page names/scope. Upload alone is not review.
- UTF-8/relative links/diff scope; docs match exact diagnostics and lifecycle.
- Record exact merge SHA and CI separately from local/PR checks; accepted closure
  required before issue completion. No main/release/tag changes.
