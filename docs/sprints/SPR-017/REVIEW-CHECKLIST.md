# SPR-017 Review Checklist

Status: proposed plan. All implementation checks pending.

- [ ] Plan approved, including intentional safe DOCX CLI stderr replacement.
- [ ] Current develop inspected; future issue and separate feature branch prepared.
- [ ] AC-01–AC-12 verified with exact evidence.
- [ ] Existing parser/run_publish signature and PDF-first precedence retained.
- [ ] Registered DOCX pipeline called once, request forwarded without fallback.
- [ ] Success stdout delayed until successful stop; operational failure exit 1.
- [ ] Parser errors exit 2 before runtime construction.
- [ ] Primary DOCX diagnostic code/stage safe; runtime/config boundary explicit.
- [ ] Expected cleanup-before-primary ordering and one primary line preserved.
- [ ] Unexpected DOCX primary cannot be masked by unexpected shutdown.
- [ ] Committed files retained on cleanup/shutdown failure; no rollback promise.
- [ ] OOXML equivalence/source fidelity verified without raw ZIP-byte assumptions.
- [ ] Legacy and new direct API contracts preserved; old coverage retained.
- [ ] HTML/PDF/batch/default runtime behavior unchanged.
- [ ] USER-GUIDE/CHANGELOG explain intentional CLI diagnostic change.
- [ ] Four CI jobs and all seven >=95% gates plus total >=99% pass.
- [ ] Real installed-wheel CLI checks and retained API smoke pass outside checkout.
- [ ] DOCX visual artifact actually reviewed on tested SHA.
- [ ] Source review and explicit merge authorization recorded before merge.
- [ ] Exact post-merge CI, acceptance/closure precede issue closure.
- [ ] main unchanged; no release or branch deletion.

Planning PR is documentation only. Implementation/merge requires a separate task.
