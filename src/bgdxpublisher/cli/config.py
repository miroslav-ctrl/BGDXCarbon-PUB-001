"""Configuration-related CLI commands."""

import sys
from pathlib import Path

from bgdxpublisher.runtime import PublisherApplication, RuntimeFoundationError


def run_config_validate(config_path: Path) -> int:
    """Validate application configuration using the runtime's service contract.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Zero when configuration is valid, otherwise one.
    """
    application = PublisherApplication(config_path=config_path)
    try:
        application.configuration.load()
    except RuntimeFoundationError as error:
        sys.stderr.write(f"Configuration is invalid: {error}\n")
        return 1
    sys.stdout.write("Configuration is valid.\n")
    return 0
