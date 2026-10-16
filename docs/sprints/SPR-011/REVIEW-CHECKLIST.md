# SPR-011 Review Checklist

- [ ] Public contracts and exclusions match IMPLEMENTATION-SPEC.md.
- [ ] AC-01 through AC-13 have concrete evidence.
- [ ] QUEUED precondition is checked before stages or transitions.
- [ ] Immutable job snapshots and exact status history are preserved.
- [ ] Pipeline causes, stage details and cleanup errors survive typed wrapping.
- [ ] Cleanup is engine-owned; no double close or premature COMPLETED.
- [ ] Each call gets a fresh context; no global mutable execution state.
- [ ] Logs exclude document values and exception messages.
- [ ] Runtime registration and empty default pipeline are tested.
- [ ] Installed-wheel API smoke test runs outside checkout.
- [ ] Existing publishing and CLI regression checks pass.
- [ ] Four CI combinations and all coverage thresholds pass.
- [ ] Implementation PR reviewed before merge to develop.
- [ ] Post-merge CI and closure evidence recorded before closing #22.

Planning documentation alone does not satisfy implementation acceptance.
