# SPR-013 Review Checklist

- [ ] AC-01: HTML dispatch resolves HtmlPublicationService only.
- [ ] AC-02: Arguments/defaults and HTML bytes remain compatible.
- [ ] AC-03: Success returns 0 and one Published: <path> line.
- [ ] AC-04: Parser failure returns 2 before publication; operational failure returns 1.
- [ ] AC-05: Safe primary diagnostic contains stable code and stage.
- [ ] AC-06: Runtime closes; simultaneous shutdown failure preserves primary error.
- [ ] AC-07: Filesystem protections and no-rollback boundary preserved.
- [ ] AC-08: DOCX/PDF/batch/direct legacy API behavior retained.
- [ ] AC-09: Installed wheel CLI works outside checkout.
- [ ] AC-10: All quality and coverage gates pass.
- [ ] Intentional safe diagnostic change documented in user guide.
- [ ] No duplicate/fallback HTML publication or cause-message exposure.
- [ ] Implementation review and authorized merge recorded.
- [ ] Post-merge verification recorded before issue #28 closure.

All items remain pending implementation.
