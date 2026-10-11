# SPR-009 verification

- [x] Windows Python 3.14.8: 221 tests; total coverage 99.81%.
- [x] Ruff, Black and MyPy pass.
- [x] OOXML reopened with python-docx: headings, Unicode, formatting, numbering,
  metadata, language, links, alternative text and absence of embedded images.
- [x] CLI success, overwrite refusal/explicit overwrite, invalid arguments,
  source aliases, missing inputs, bad UTF-8, commit failure and runtime cleanup.
- [x] Shared writer's existing HTML race/permission/failure tests remain passing.
- [ ] Exact PR head: Windows/Linux Python 3.13/3.14 and installed-wheel CI.
- [ ] Rendered acceptance sample: every page visually inspected.

The bundled local runtime has python-docx, but no LibreOffice executable on
Windows. Linux CI generates a DOCX/PDF/page PNG verification artifact; PDF here
is a test intermediate, not a new product command.
