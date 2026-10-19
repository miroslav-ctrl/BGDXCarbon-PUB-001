# SPR-018 Review Checklist

Status: proposed plan; all implementation acceptance pending.

- [ ] Plan approved with API-only scope; CLI migration explicitly deferred.
- [ ] Then-current develop inspected; separate implementation issue/branch created.
- [ ] AC-01–AC-12 mapped to exact executed evidence.
- [ ] Typed consistent envelopes/errors; safe codes/stages and internal causes.
- [ ] Fresh document/job/context, deterministic stages and one read/render/write.
- [ ] Metadata/path validation precedes reads; source/output protections retained.
- [ ] PdfRenderer/fonts/writer reused without policy changes or legacy fallback.
- [ ] Differential PDF comparison and narrowly justified volatility policy verified.
- [ ] Unsupported glyph/font/layout errors are safe render-stage failures.
- [ ] Cleanup once; committed output retained on postcommit failure; no rollback.
- [ ] New logs exclude raw paths/title/body/bytes/cause; legacy diagnostics unchanged.
- [ ] Runtime registration alongside legacy; caller owns lifecycle, no CLI change.
- [ ] Legacy API/CLI, PDF-first precedence and unrelated command tests retained.
- [ ] Total >=99%, existing seven plus new eighth >=95% gate in four matrix jobs.
- [ ] Fresh installed-wheel new API plus existing command/API smoke checks pass.
- [ ] Actual new-API single/multipage visual artifacts inspected and recorded.
- [ ] README/release guide current integration descriptions aligned; history preserved.
- [ ] Formal review and explicit owner merge authorization recorded.
- [ ] Exact post-merge CI/acceptance/closure precede implementation issue completion.
- [ ] No main change, release/tag, version/dependency change or branch deletion.

This submission is documentation only; implementation requires a separate task.
