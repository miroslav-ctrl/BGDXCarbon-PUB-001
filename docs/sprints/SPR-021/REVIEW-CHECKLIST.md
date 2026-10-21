# SPR-021 Review Checklist

Status: implementation submitted for Draft review; final acceptance/closure pending.

- [x] Owner accepted bounded release1.2.0 scope; included in this documentation PR.
- [x] Current develop/SPR-020 closure/baseline CI inspected; no open work at baseline.
- [x] API-only SPR-020 reused; new CLI-only scope and explicit exclusions defined.
- [x] Exact parser, stdout/stderr, preflight/item diagnostic contracts specified.
- [x] Expected/unexpected runtime shutdown/primary precedence matrix explicit.
- [x] Direct API/old CLI/engine/writer compatibility and quality gates retained.
- [x] Owner approval of SPR-021 plan and separately authorized plan merge (#58).
- [x] Separate implementation authorization/new issue#59/branch from current develop.
- [ ] AC-01 through AC-10 mapped to actual executed implementation evidence.
- [ ] Four matrix jobs/full/static/total>=99% and all nine gates>=95% pass.
- [ ] Fresh installed-wheel and actual new CLI/config/error/runtime checks pass.
- [ ] Actual batch CLI DOCX artifact/all sample pages inspected and recorded.
- [ ] Current user docs/examples/changelog/release guide aligned; history intact.
- [ ] Formal implementation review/owner acceptance/authorized merge/exact post-merge CI.
- [ ] Accepted closure documentation before implementation issue completion.
- [x] Implementation confined to new CLI adapter/entry; version/dependencies/main unchanged; no merge/release.

Plan CI does not complete implementation acceptance. Codex formal COMMENT reviews
are disclosed as such; owner approval and later execution authorizations are separate.
