"""Doctor command execution and presentation."""

from pathlib import Path
from typing import TextIO

from bgdxpublisher.diagnostics import DiagnosticReport, DiagnosticService
from bgdxpublisher.diagnostics.checks import default_diagnostic_checks


def format_report(report: DiagnosticReport) -> str:
    """Format a diagnostic report for the human-readable console."""
    lines = ["BGDXCarbon Publisher Suite", ""]
    for result in report.results:
        dots = "." * max(1, 22 - len(result.name))
        lines.append(f"{result.name} {dots} {result.status.value}")
    overall = (
        "NOT READY"
        if not report.ready
        else (
            "READY WITH WARNINGS"
            if report.overall_status.value == "WARNING"
            else "READY"
        )
    )
    lines.extend(("", f"Overall .............. {overall}"))
    return "\n".join(lines) + "\n"


def run_doctor(
    output: TextIO,
    config_path: Path,
    service: DiagnosticService | None = None,
) -> int:
    """Execute diagnostic checks, present their report, and return an exit code."""
    diagnostic_service = (
        DiagnosticService(default_diagnostic_checks(config_path))
        if service is None
        else service
    )
    report = diagnostic_service.run()
    output.write(format_report(report))
    return report.exit_code
