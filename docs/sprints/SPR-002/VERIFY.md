# SPR-002 Verification

Run from the repository root with Python 3.13 or newer and the development
extras installed:

```sh
ruff check .
black --check .
mypy src
pytest
pytest --cov=bgdxpublisher --cov-report=term-missing
```

Verify the installed commands:

```sh
bgdxpublisher --help
bgdxpublisher version
bgdxpublisher doctor
bgdxpublisher config validate
bgdxpublisher runtime status
```

Use `--config PATH` with `doctor`, `config validate`, and `runtime status` to
verify an alternate configuration.

Default configuration is packaged as `bgdxpublisher.config/default.yaml` and read
with `importlib.resources`. The installed commands (including no-argument startup)
work from an unrelated directory without a local `configs/default.yaml`.
Explicit `--config PATH` overrides the resource; relative explicit paths remain
relative to the caller's working directory. Environment overrides still apply.

`version` reports configured application name/version, the running Python version,
and runtime environment. No-argument startup logs
`BGDXCarbon Publisher Suite <version> started.`

`doctor` ends with `Overall .............. READY` and exits 0 unless a mandatory
diagnostic fails, in which case it prints `Overall .............. FAILED` and
exits 1. Warnings alone remain READY.

SPR-002 intentionally catches broad `Exception` only at the diagnostic boundary,
converting unexpected errors into structured `DiagnosticResult` failures so the
remaining checks can run. Best-effort diagnostic cleanup preserves the original
failure. This does not broaden exception handling elsewhere; existing SPR-001
lifecycle exception and cleanup contracts remain unchanged.

`runtime status` reports the initialized CONFIGURED state captured before its
temporary start/stop cleanup. It does not report the final STOPPED cleanup state.
