# SPR-015 Review Checklist

Status: implementation prepared for review. See IMPLEMENTATION-EVIDENCE.md; implementation review/CI/closure checks remain pending.

- [x] Plan approved, including safe ordinal diagnostics and shutdown output policy (owner approval and merged plan PR #35).
- [ ] AC-01 through AC-12 verified with exact evidence in ACCEPTANCE.md.
- [ ] Existing parser/signature/defaults unchanged.
- [ ] BatchHtmlPublicationService resolved once; legacy path forbidden in selection tests.
- [ ] Typed terminal outcomes drive counts and safe diagnostics.
- [ ] Primary error survives shutdown failure; unexpected exceptions propagate.
- [ ] Committed files retained on cleanup/index/runtime failure; no rollback promise.
- [ ] Existing direct APIs and unrelated commands unchanged.
- [ ] CLI-facing stderr expectation changes are intentional and documented.
- [ ] Four CI jobs, total >=99% and six independent >=95% gates pass.
- [ ] Fresh installed-wheel checks execute outside checkout on all four jobs.
- [ ] User guide and CHANGELOG explain intentional diagnostic/shutdown differences.
- [ ] Implementation diff is limited to approved scope and targets current develop.
- [ ] Actual source review and authorization are recorded before merge.
- [ ] Separately authorized merge and exact successful post-merge CI recorded.
- [ ] Final closure recorded before closing the future implementation issue.
- [ ] main remains unchanged.

Implementation PR includes the adapter, focused regressions, installed-wheel smoke, workflow invocation and documentation. No merge or final acceptance is claimed.
