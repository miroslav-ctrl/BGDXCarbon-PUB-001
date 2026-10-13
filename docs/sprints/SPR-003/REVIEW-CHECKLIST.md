# SPR-003 Review Checklist

- [ ] Document identifiers, supported types, timestamps, titles, source references,
  and deeply immutable metadata are validated.
- [ ] Document/job validation errors have stable codes and retain structured details.
- [ ] Job transitions enforce the required sequence and controlled failure path.
- [ ] Pipeline stage order and input/output contracts are deterministic and explicit.
- [ ] Pipeline failures propagate with structured results, causes, and cleanup outcomes.
- [ ] Pipeline logging contains job/stage identifiers and never document content.
- [ ] Empty pipeline handling and side-effect-free execution are verified.

- [ ] CLI delegates publishing to a registered service.
- [ ] Immutable request/result contracts and domain errors are reviewed.
- [ ] Unicode, supported Markdown and unsafe input behaviors are verified.
- [ ] No overwrite without explicit permission, including creation races.
- [ ] Input and previous output survive rendering/write failure.
- [ ] Runtime cleanup is verified after success and operational failure.
- [ ] Existing SPR-001/SPR-002 regression tests pass.
- [ ] Windows/Linux and Python 3.13/3.14 CI pass with coverage >=99%.
- [ ] Installed wheel publishes from outside the repository.
- [ ] Representative HTML is manually inspected before approval.
