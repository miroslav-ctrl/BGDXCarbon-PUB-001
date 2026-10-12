# SPR-010 verification

- [x] Windows Python 3.14.8: 246 tests pass; coverage 99.84%; PDF module 100%.
- [x] Ruff and MyPy pass; Black formatting applied.
- [x] Actual PDFs parsed: title/language, A4 size, Unicode text, independent
  numbering, inline styles, safe URI annotations, embedded fonts/Unicode maps,
  no image resources or script/open actions.
- [x] Long paragraphs/code paginate and retain every character and final markers.
- [x] CLI/paths: aliases, missing input/parent, overwrite, invalid arguments,
  bad UTF-8, unsupported glyphs, commit/layout/font failure and runtime closure.
- [x] HTML and DOCX regression tests pass, including shared atomic writer policy.
- [x] Bundled ReportLab 4.4.9 generates sample and stress PDFs; Poppler renders
  their 1 + 3 pages. Every page inspected: Unicode, links, formatting, nesting,
  list restart, code, pagination; no clipping/overlap. pdfplumber verifies every
  character bounding box stays inside the page margins.
- [ ] Exact PR head: Windows/Linux Python 3.13/3.14 quality and installed-wheel CI.
- [ ] Linux-generated PDF acceptance sample visually inspected.

ReportLab 4.5.1 used by repository tests; lower-bound 4.4.9 used by bundled
artifact runtime. Fonts are packaged with full attribution/license and checksum
provenance. Original user checkout and published v1.0.0 release are untouched.
