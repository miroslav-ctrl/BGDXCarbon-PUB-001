"""Doctor command."""

import sys
from pathlib import Path

from bgdxpublisher.diagnostics import DiagnosticService, default_diagnostic_checks


def run_doctor(config_path: Path) -> int:
    """Run runtime diagnostics and print their results.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        One if a mandatory diagnostic failed, otherwise zero.
    """
    report = DiagnosticService(default_diagnostic_checks(config_path=config_path)).run()
    for result in report.results:
        sys.stdout.write(f"{result.status.value}: {result.name}: {result.message}\n")
    return report.exit_code
