"""Argument parsing and command dispatch for the publisher CLI."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Callable, cast

from bgdxpublisher.logging import LoggingService
from bgdxpublisher.runtime import PublisherApplication, RuntimeFoundationError

from .config import run_config_validate
from .doctor import run_doctor
from .runtime import run_runtime_status
from .version import run_version

CommandHandler = Callable[[argparse.Namespace], int]


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser and all supported subcommands."""
    parser = argparse.ArgumentParser(
        prog="bgdxpublisher",
        description="Enterprise Publisher Suite command-line interface.",
    )
    commands = parser.add_subparsers(dest="command")

    version_parser = commands.add_parser(
        "version", help="Show the application version."
    )
    version_parser.set_defaults(handler=lambda _args: run_version())

    doctor_parser = commands.add_parser(
        "doctor", help="Run runtime and workspace diagnostics."
    )
    doctor_parser.add_argument("--config", type=Path, default=None)
    doctor_parser.set_defaults(handler=lambda args: run_doctor(args.config))

    config_parser = commands.add_parser("config", help="Inspect configuration.")
    config_commands = config_parser.add_subparsers(dest="config_command")
    validate_parser = config_commands.add_parser(
        "validate", help="Validate the application configuration."
    )
    validate_parser.add_argument("--config", type=Path, default=None)
    validate_parser.set_defaults(handler=lambda args: run_config_validate(args.config))

    runtime_parser = commands.add_parser("runtime", help="Inspect the runtime.")
    runtime_commands = runtime_parser.add_subparsers(dest="runtime_command")
    status_parser = runtime_commands.add_parser(
        "status", help="Show initialized runtime status."
    )
    status_parser.add_argument("--config", type=Path, default=None)
    status_parser.set_defaults(handler=lambda args: run_runtime_status(args.config))
    return parser


def _start_default_application() -> int:
    """Preserve the original no-argument application startup behavior."""
    application = PublisherApplication()
    try:
        application.initialize()
        application.start()
        application.context.services.resolve(LoggingService).logger.info(
            "BGDXCarbon Publisher Suite %s started.",
            application.context.metadata.version,
        )
        application.stop()
    except RuntimeFoundationError as error:
        sys.stderr.write(f"Unable to start application: {error}\n")
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI with supplied arguments or the process command line.

    Args:
        argv: Optional command-line arguments, excluding the executable name.

    Returns:
        The selected command's exit code.
    """
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments:
        return _start_default_application()

    parser = build_parser()
    parsed = parser.parse_args(arguments)
    handler = getattr(parsed, "handler", None)
    if handler is None:
        parser.print_help(file=sys.stdout)
        return 0
    return cast(CommandHandler, handler)(parsed)
