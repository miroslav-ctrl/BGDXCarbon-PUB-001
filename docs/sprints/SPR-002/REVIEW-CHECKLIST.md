# SPR-002 Review Checklist

- [ ] CLI help exposes all required commands and nested subcommands.
- [ ] Version reports application name/version, Python version, and environment.
- [ ] Doctor reports structured checks and aggregate readiness.
- [ ] Mandatory failures return exit code 1; warnings alone return 0.
- [ ] Configuration validation reuses the application and configuration services.
- [ ] Runtime status reads SPR-001 metadata and lifecycle state.
- [ ] Diagnostic execution is separate from CLI presentation.
- [ ] Existing SPR-001 contracts and tests remain unchanged and pass.
- [ ] No new third-party dependency or out-of-scope feature is introduced.
- [ ] Python 3.13 quality and coverage gates pass.
