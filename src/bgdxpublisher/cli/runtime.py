"""Runtime-related CLI commands."""

import sys
from pathlib import Path

from bgdxpublisher.runtime import PublisherApplication, RuntimeFoundationError


def run_runtime_status(config_path: Path) -> int:
    """Initialize the application and report its runtime metadata and state.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Zero when runtime status is available, otherwise one.
    """
    application = PublisherApplication(config_path=config_path)
    try:
        application.initialize()
        metadata = application.context.metadata
        state = application.state
        application.start()
        application.stop()
    except RuntimeFoundationError as error:
        sys.stderr.write(f"Unable to read runtime status: {error}\n")
        return 1
    sys.stdout.write(
        f"Application: {metadata.name}\n"
        f"Version: {metadata.version}\n"
        f"Environment: {metadata.environment}\n"
        f"State: {state.name}\n"
    )
    return 0
