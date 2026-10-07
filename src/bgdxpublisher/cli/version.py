"""Version command presentation."""

import sys
from collections.abc import Mapping
from typing import TextIO

from bgdxpublisher.version import __version__


def show_version(
    output: TextIO,
    environ: Mapping[str, str] | None = None,
    python_version: str | None = None,
) -> int:
    """Write application and runtime version information."""
    environment = ({} if environ is None else environ).get(
        "BGDXPUBLISHER_ENV", "development"
    )
    interpreter_version = (
        sys.version.split()[0] if python_version is None else python_version
    )
    output.write("Application: BGDXCarbon Publisher Suite\n")
    output.write(f"Application version: {__version__}\n")
    output.write(f"Python version: {interpreter_version}\n")
    output.write(f"Runtime environment: {environment}\n")
    return 0
