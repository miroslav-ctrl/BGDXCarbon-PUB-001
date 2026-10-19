# SPR-016 Review Checklist

Status: implemented for review. Final review/CI/visual/post-merge acceptance checks remain pending; see IMPLEMENTATION-EVIDENCE.md.

- [x] Plan approved, including API-only scope and OOXML comparison policy (PR #38).
- [ ] Current develop inspected before implementation; separate feature branch/issue.
- [ ] AC-01 through AC-12 verified with exact evidence.
- [ ] New service registered alongside legacy DocxPublishingService.
- [ ] CLI still selects legacy DOCX; parser/output/exits/lifecycle unchanged.
- [ ] Legacy direct API/PublishingError/cause and unrelated routes unchanged.
- [ ] Typed validate/read/render/write contracts and terminal invariants enforced.
- [ ] Fresh IDs/contexts; no duplicate renderer/write or fallback publication.
- [ ] Source, overwrite, alias, symlink, race and permission protections retained.
- [ ] Failed postcommit cleanup retains output without success/rollback claim.
- [ ] Safe logs apply to new route without changing legacy diagnostics.
- [ ] OOXML equivalence verified without brittle raw ZIP-byte comparison.
- [ ] Existing renderer unchanged; no new dependencies or version bump.
- [ ] Total >=99% and seven separate >=95% package gates pass in four CI jobs.
- [ ] Fresh installed-wheel API and existing CLI checks pass outside checkout.
- [ ] DOCX visual artifact actually reviewed and recorded.
- [ ] Source review and explicit merge authorization recorded before merge.
- [ ] Exact post-merge CI, acceptance and closure recorded before issue closure.
- [ ] main unchanged; no release or branch deletion.

Implementation PR contains the new package/registration, tests, workflow/example and documentation. No final acceptance or merge is claimed.
