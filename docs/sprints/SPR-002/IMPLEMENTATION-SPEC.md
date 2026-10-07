# SPR-002 Implementation Specification

## Architecture

The CLI delegates configuration validation and runtime initialization to
`PublisherApplication`. The application continues to use the SPR-001
`ConfigurationService`, logging factory, service registry, and `RuntimeContext`.
Diagnostics checks return data models only; CLI modules render their results.

The CLI uses Python's standard-library `argparse` and `pathlib`. The installed
entry point is declared in `pyproject.toml`; no third-party dependency or
architecture replacement is introduced.

## Public diagnostic API

- `DiagnosticStatus`: `PASS`, `WARNING`, or `FAIL`.
- `DiagnosticResult`: check name, outcome, explanatory message, and mandatory
  flag.
- `DiagnosticReport`: ordered check results with aggregate readiness and
  process exit code.
- `DiagnosticService`: runs an injected ordered collection of checks and
  converts an unexpected check exception into a structured failure.

## Default checks

1. Require Python 3.13 or newer.
2. Load and validate configuration via the application facade.
3. Initialize and close the standard logging service.
4. Register and resolve a service using the existing service registry.
5. Initialize, start, and stop the publisher runtime.
6. Confirm that the workspace is an accessible directory.

All default checks are mandatory. A non-mandatory failure remains available in
the report but does not prevent readiness; warnings likewise keep doctor exit
status zero.

## Configuration and lifecycle behavior

The configuration command calls `PublisherApplication.validate_configuration`,
which delegates to the injected SPR-001 `ConfigurationService`. Runtime status
captures metadata and lifecycle state from the initialized application context,
then starts and stops the runtime to release owned logging resources.
