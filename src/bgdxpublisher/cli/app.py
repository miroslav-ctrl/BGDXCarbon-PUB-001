"""Command-line argument parsing and command dispatch."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from .config import validate_configuration
from .doctor import run_doctor
from .runtime import show_runtime_status
from .version import show_version

_DEFAULT_CONFIG = Path("configs/default.yaml")


def build_parser() -> argparse.ArgumentParser:
    """Create the enterprise publisher command parser."""
    parser = argparse.ArgumentParser(
        prog="bgdxpublisher", description="BGDXCarbon Publisher Suite"
    )
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("version", help="show application and runtime versions")

    doctor = commands.add_parser("doctor", help="run runtime diagnostic checks")
    doctor.add_argument("--config", type=Path, default=_DEFAULT_CONFIG)

    config = commands.add_parser("config", help="configuration commands")
    config_commands = config.add_subparsers(dest="config_command")
    validate = config_commands.add_parser("validate", help="validate configuration")
    validate.add_argument("--config", type=Path, default=_DEFAULT_CONFIG)

    runtime = commands.add_parser("runtime", help="runtime commands")
    runtime_commands = runtime.add_subparsers(dest="runtime_command")
    status = runtime_commands.add_parser("status", help="show runtime status")
    status.add_argument("--config", type=Path, default=_DEFAULT_CONFIG)
    return parser


def main(
    argv: Sequence[str] | None = None,
    output: TextIO | None = None,
) -> int:
    """Run the command-line interface and return its process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    console = sys.stdout if output is None else output

    if args.command is None:
        parser.print_help(file=console)
        return 0
    if args.command == "version":
        return show_version(console)
    if args.command == "doctor":
        return run_doctor(console, args.config)
    if args.command == "config" and args.config_command == "validate":
        return validate_configuration(console, args.config)
    if args.command == "runtime" and args.runtime_command == "status":
        return show_runtime_status(console, args.config)
    parser.error("a command is required")
