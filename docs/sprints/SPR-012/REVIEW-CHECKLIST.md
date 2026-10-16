# SPR-012 Review Checklist

- [ ] AC-01: Successful lifecycle and exact PublishResult path/UTF-8 byte count.
- [ ] AC-02: Deterministic typed validate/read/render/write order.
- [ ] AC-03: Byte-equivalent output to legacy HTML for title/lang/theme/TOC.
- [ ] AC-04: Unchanged source; UTF-8/BOM and Serbian Latin/Cyrillic.
- [ ] AC-05: Validation/read/render/write failures produce FAILED and retain cause without partial result.
- [ ] AC-06: Overwrite, alias/symlink, race and source protections retained.
- [ ] AC-07: Temporary resources cleaned; committed output retained if later cleanup fails.
- [ ] AC-08: Isolated contexts/jobs and exactly one read/render/write per successful call.
- [ ] AC-09: Safe logs without content, paths or raw exception messages.
- [ ] AC-10: Runtime and installed-wheel success/failure outside checkout.
- [ ] AC-11: Legacy CLI/HTML/DOCX/PDF/batch unchanged.
- [ ] AC-12: All quality and independent coverage gates pass.
- [ ] Commit boundary and no-rollback limitation explicitly tested and documented.
- [ ] Existing renderer/writer reused without duplicate publication flow.
- [ ] SPR-011 API and default runtime coordinator remain compatible.
- [ ] Implementation PR reviewed before merge to develop.
- [ ] Exact post-merge CI and closure evidence recorded before closing #25.

All items remain pending implementation.
