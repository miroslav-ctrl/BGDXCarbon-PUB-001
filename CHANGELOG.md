# Changelog

## 1.2.0 — 2026-10-22

- Complete single-document and batch CLI/API coverage for HTML, DOCX and PDF.
  New commands: publish-docx-batch and publish-pdf-batch; new registered DOCX/PDF
  single and batch pipeline services. Existing command options and direct legacy
  APIs remain supported; HTML index/theme/navigation behavior is preserved.
- Connect publication commands to typed job orchestration with fresh per-call
  contexts, immutable terminal outcomes and derived batch counts.
- Use safe code/stage/ordinal reports for expected operational failures;
  deterministic guarded batch preflight and independent atomic commits. Expected
  item failures continue; unexpected external failures stop later attempts.
- Buffer publication success reports until runtime shutdown succeeds. Preserve
  primary exceptions and committed files on cleanup failure; no batch rollback.
- Retain total coverage>=99% and ten independent package>=95% gates across
  Windows/Linux Python 3.13/3.14. Verify actual installed wheel and source archive,
  CLI/direct API fidelity, packaged configuration/fonts/licenses/checksums and
  all retained DOCX/PDF preview artifacts.
- Synchronize package/runtime/default configuration identity to 1.2.0 and update
  user documentation/examples. Release assets are distributed through GitHub.

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

