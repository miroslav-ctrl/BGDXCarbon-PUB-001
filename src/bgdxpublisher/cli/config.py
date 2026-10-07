"""Configuration validation command."""

from pathlib import Path
from typing import TextIO

from bgdxpublisher.config import ConfigurationError
from bgdxpublisher.runtime import PublisherApplication


def validate_configuration(
    output: TextIO,
    config_path: Path,
    application_factory: type[PublisherApplication] = PublisherApplication,
) -> int:
    """Validate configuration through the publisher application layer."""
    application = application_factory(config_path=config_path)
    try:
        application.validate_configuration()
    except ConfigurationError as error:
        output.write(f"Configuration validation failed: {error}\n")
        return 1
    output.write("Configuration is valid.\n")
    return 0
