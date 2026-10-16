# SPR-014 Review Checklist

- [ ] AC-01: Legacy nonrecursive discovery, case-insensitive .md selection and ordering.
- [ ] AC-02: Independent jobs/contexts per attempted item.
- [ ] AC-03: Byte-equivalent HTML for identical inputs/options.
- [ ] AC-04: Stem collisions and index.md conflict rejected before publication.
- [ ] AC-05: Expected item failure does not stop remaining items.
- [ ] AC-06: Source/overwrite/alias/symlink/race protections retained.
- [ ] AC-07: Index includes completed items only; independent index failure preserves documents.
- [ ] AC-08: Postcommit cleanup failure is FAILED and excluded from index without rollback.
- [ ] AC-09: Safe logs and exactly one publication attempt per item.
- [ ] AC-10: Runtime and installed wheel support success/partial/index failure.
- [ ] AC-11: Existing CLI and direct APIs unchanged.
- [ ] AC-12: Quality and coverage pass in four environments.
- [ ] Preflight, per-item and index error contracts remain distinct.
- [ ] Aggregate invariants reject inconsistent outcomes.
- [ ] No rollback claim after atomic commit.
- [ ] No CLI route migration or legacy API break.
- [ ] Review, authorized merge and post-merge evidence recorded before #31 closure.

All items remain pending implementation.
