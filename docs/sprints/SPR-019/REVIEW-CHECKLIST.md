# SPR-019 Review Checklist

Status: implemented for review; final review/CI/post-merge acceptance pending. See IMPLEMENTATION-EVIDENCE.md.

- [x] Plan approved including intentional safe PDF CLI stderr replacement.
- [ ] Then-current develop inspected; separate implementation issue/branch.
- [ ] AC-01–AC-12 mapped to actual exact-SHA evidence.
- [ ] Parser/signature/defaults and PDF-first both-flags preserved.
- [ ] Registered PDF pipeline called once/exact request/no legacy fallback.
- [ ] Published stdout only after successful stop; exits 0/1/2 as specified.
- [ ] Structured safe PDF code/stage; runtime/config diagnostic boundary explicit.
- [ ] Unsupported glyph detail removed only from new CLI diagnostic; direct API intact.
- [ ] Expected stop cleanup-before-primary order/count and no false success.
- [ ] Unexpected-primary/stop matrix and handled-typed/no-active-primary case verified.
- [ ] Existing DOCX primary protection and unrelated route behavior preserved.
- [ ] PDF equivalence/source safety and overwrite/filesystem protections retained.
- [ ] Engine cleanup once/FAILED/retained committed file; no rollback promise.
- [ ] Legacy and pipeline direct API contracts/cause/logging preserved.
- [ ] Update only obsolete PDF CLI route assertions; preserve useful tests/history.
- [ ] User guide/changelog/current docs explain intentional diagnostic boundary.
- [ ] Four CI jobs, total >=99%, all eight independent >=95% gates pass.
- [ ] Real installed-wheel CLI and retained API/other-command smoke pass.
- [ ] Actual migrated-CLI PDF artifact inspected; API multipage/DOCX checks retained.
- [ ] Formal source review and explicit owner merge authorization recorded.
- [ ] Exact post-merge CI/acceptance/closure before issue completion.
- [ ] No main change, release/tag, version/dependency change or branch deletion.

Implementation prepared under #51. No merge or closure claimed.
