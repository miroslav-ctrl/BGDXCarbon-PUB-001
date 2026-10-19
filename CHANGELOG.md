# Changelog

## Unreleased

- Route the existing `publish-docx` CLI through the registered DOCX job pipeline.
  Success output/options remain unchanged; expected operational errors now use
  `DOCX_PUBLICATION_FAILED stage=<stage>` with exit 1 rather than raw causes.
  Direct DOCX APIs remain unchanged. Runtime shutdown failures suppress success
  output, retain committed files and preserve the primary DOCX failure.

- Add a separately registered DOCX job pipeline API with typed stages, immutable
  execution results, safe failure diagnostics and independent per-call jobs.
  Direct `DocxPublishingService` retains its legacy route; CLI integration is
  listed separately above.

- Route `publish-batch` through the registered batch HTML job pipeline. Preserve
  command options, document/index bytes and success output; expected failures now
  report stable codes and item ordinals instead of source paths/raw causes.
- Delay batch stdout until runtime shutdown succeeds. Shutdown failure returns 1
  without success/summary stdout, while committed files and primary diagnostics
  remain intact. Legacy direct batch API and other commands retain their routes.

## 1.1.0 — 2026-10-14

- Add immutable document models, structured validation, publisher job lifecycle,
  and deterministic sequential pipeline execution with typed stage contracts,
  failure reporting, cleanup, and safe structured logging.

- Add `publish-pdf` with selectable Unicode text, embedded licensed fonts,
  safe links, print layout, automatic pagination and atomic output writing.

- Add `publish-docx` for editable Word output with metadata, Unicode, headings,
  inline formatting, lists, quotations, code and safe external links.
- Share atomic binary output writing with HTML; preserve overwrite and permissions.

## 1.0.0 — 2026-10-11

- First stable HTML CLI release: documentation, examples, synchronized version
  metadata, and verified GitHub release assets with SHA-256 checksums.

- Added SPR-008 optional batch HTML index with safe relative links to successful outputs.

- Added SPR-007 non-recursive batch Markdown publishing with per-file results.

- Added SPR-006 optional heading table of contents with unique Unicode targets.

- Added SPR-005 embedded light/dark HTML themes with validated CLI selection.

- Added SPR-004 HTML title and language CLI options with metadata validation.

- Implemented the SPR-001 runtime foundation: configuration, logging, typed
  service registry, runtime lifecycle, and publisher application orchestration.
- Added subsystem tests and sprint implementation documentation.
- Added the SPR-002 enterprise CLI commands and runtime diagnostics.
- Added SPR-003 Markdown-to-HTML publishing with explicit overwrite protection,
  atomic output commits, regression tests and installed-wheel CI checks.

