"""Version command."""

import sys

from bgdxpublisher.version import __version__


def run_version() -> int:
    """Write the application version and return a successful exit code."""
    sys.stdout.write(f"BGDXCarbon Publisher Suite {__version__}\n")
    return 0
