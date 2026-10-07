"""Runtime status command."""

from pathlib import Path
from typing import TextIO

from bgdxpublisher.runtime import PublisherApplication, RuntimeFoundationError


def show_runtime_status(
    output: TextIO,
    config_path: Path,
    application_factory: type[PublisherApplication] = PublisherApplication,
) -> int:
    """Initialize the runtime and display its application metadata and state."""
    application = application_factory(config_path=config_path)
    try:
        application.initialize()
    except RuntimeFoundationError as error:
        output.write(f"Runtime initialization failed: {error}\n")
        return 1

    metadata = application.context.metadata
    state = application.state
    try:
        application.start()
        application.stop()
    except RuntimeFoundationError as error:
        output.write(f"Runtime shutdown failed: {error}\n")
        return 1
    output.write(f"Application: {metadata.name}\n")
    output.write(f"Version: {metadata.version}\n")
    output.write(f"Environment: {metadata.environment}\n")
    output.write(f"Runtime state: {state.name}\n")
    return 0
