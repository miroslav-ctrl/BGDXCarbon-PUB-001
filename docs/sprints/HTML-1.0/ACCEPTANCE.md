# HTML 1.0 acceptance

Scope: existing HTML CLI capabilities from SPR-001 through SPR-008. Final work
combines documentation/examples, version consistency and release preparation.
PDF/DOCX, custom templates, GUI and hosting are future work.

User acceptance already confirmed document themes, Unicode rendering, heading
navigation, batch publishing/overwrite behavior, and index links in both themes.
Release preparation changes no visual rendering or publishing behavior.

- [x] Final version 1.0.0 local quality/coverage checks pass (203 tests, 99.77%).
- [x] Fresh wheel and source distribution build successfully; metadata, source contents and SHA-256 verified.
- [x] Installed wheel outside checkout passes CLI and examples (Windows, Python 3.14.8).
- [ ] Final PR head passes Windows/Linux, Python 3.13/3.14 CI.
- [ ] Release PR merged into develop.
- [ ] v1.0.0 tag points to the reviewed merge commit.
- [ ] Release workflow verification passes and GitHub assets are published.
