# SPR-009 review checklist

- [x] DOCX command is explicit and does not change HTML argument defaults.
- [x] Title/language validation and expected-error exit codes are preserved.
- [x] Inline styles, independent lists, code and multilingual text are editable.
- [x] Unsafe/unsupported targets remain text and images are not fetched.
- [x] Source and previous output survive expected failures.
- [x] Atomic binary output reuses the HTML filesystem policy.
- [ ] CI and rendered page acceptance recorded in VERIFY.md.
