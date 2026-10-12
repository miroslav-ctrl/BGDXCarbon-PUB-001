# SPR-009 verification

- [x] Windows Python 3.14.8: 221 tests; total coverage 99.81%.
- [x] Ruff, Black and MyPy pass.
- [x] OOXML reopened with python-docx: headings, Unicode, formatting, numbering,
  metadata, language, links, alternative text and absence of embedded images.
- [x] CLI success, overwrite refusal/explicit overwrite, invalid arguments,
  source aliases, missing inputs, bad UTF-8, commit failure and runtime cleanup.
- [x] Shared writer's existing HTML race/permission/failure tests remain passing.
- [x] Code revision `5320535`: Windows/Linux Python 3.13/3.14 and installed-wheel
  CI pass (run 38153752030). Subsequent changes record evidence only.
- [x] Rendered acceptance sample: its single page visually inspected, including
  Unicode, heading hierarchy, inline formatting, links, nested bullets,
  independent ordered-list restart, quotations and code; no clipping or overlap.

The bundled local runtime has python-docx, but no LibreOffice executable on
Windows. Linux CI generates a DOCX/PDF/page PNG verification artifact; PDF here
is a test intermediate, not a new product command.
