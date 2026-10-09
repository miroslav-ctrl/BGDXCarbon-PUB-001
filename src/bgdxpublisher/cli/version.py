"""Version command."""

import platform
import sys

from bgdxpublisher.runtime import PublisherApplication, RuntimeFoundationError


def run_version() -> int:
    """Report application identity, Python version, and runtime environment.

    Returns:
        Zero on success, or one if configuration cannot be loaded.
    """
    application = PublisherApplication()
    try:
        settings = application.configuration.load()
    except RuntimeFoundationError as error:
        sys.stderr.write(f"Unable to read version information: {error}\n")
        return 1
    sys.stdout.write(
        f"Application: {settings.app.name}\n"
        f"Version: {settings.app.version}\n"
        f"Python: {platform.python_version()}\n"
        f"Environment: {settings.runtime.environment}\n"
    )
    return 0
