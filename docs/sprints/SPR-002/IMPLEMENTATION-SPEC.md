# SPR-002 Implementation Specification

## Architecture

The CLI is an `argparse` adapter. Configuration and runtime commands delegate
to `PublisherApplication`; diagnostic checks resolve services from its
`RuntimeContext` and use its existing configuration, lifecycle, logging, and
registry implementations.

## Diagnostic contract

`DiagnosticStatus` has `PASS`, `WARNING`, and `FAIL` values. Immutable
`DiagnosticResult` values describe each check, and `DiagnosticReport` computes
the aggregate status and exit code. `DiagnosticService` runs every registered
check and converts unexpected check exceptions into mandatory failures.

Python version, configuration, logging, registry, and runtime checks are
mandatory. Workspace accessibility is reported as a non-mandatory warning
when unavailable.

## CLI behavior

The `bgdxpublisher` project script and `python -m bgdxpublisher` dispatch to
the same CLI. `--config PATH` selects an alternate YAML configuration for
`doctor`, `config validate`, and `runtime status`. The pre-existing no-argument
startup behavior is retained.
