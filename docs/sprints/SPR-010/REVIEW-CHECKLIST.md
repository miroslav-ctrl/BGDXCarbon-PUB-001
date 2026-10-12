# SPR-010 review checklist

- [x] PDF command is explicit; HTML/DOCX defaults are unchanged.
- [x] Direct rendering needs no installed office/browser application.
- [x] Font provenance/license/package data and supported Unicode are verified.
- [x] Text/formatting, lists, code, links and pagination are verified in actual PDF.
- [x] Images/raw HTML/unsupported links remain visible safe fallbacks.
- [x] Source/previous output and runtime cleanup retain existing contracts.
- [x] All local rendered pages are clean and inside margins.
- [ ] Remote CI and Linux sample inspection recorded in VERIFY.md.
- [x] DOCX dependency and subsequent develop retargeting are documented.
