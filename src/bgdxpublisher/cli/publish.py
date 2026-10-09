"""CLI adapter for document publishing."""

import sys
from pathlib import Path

from bgdxpublisher.publishing import PublishingService, PublishRequest
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


def run_publish(
    source: Path,
    output: Path,
    overwrite: bool,
    config_path: Path | None,
    title: str | None = None,
    language: str = "und",
) -> int:
    """Delegate to the registered publisher and close runtime on failure too."""
    application = PublisherApplication(config_path=config_path)
    result = None
    failure: RuntimeFoundationError | None = None
    try:
        application.initialize()
        application.start()
        service = application.context.services.resolve(PublishingService)
        result = service.publish(
            PublishRequest(source, output, overwrite, title, language)
        )
    except RuntimeFoundationError as error:
        failure = error
    finally:
        if application.state in (RuntimeState.CONFIGURED, RuntimeState.RUNNING):
            try:
                application.stop()
            except RuntimeFoundationError as error:
                sys.stderr.write(f"Runtime cleanup failed: {error}\n")
                failure = failure or error
    if failure is not None:
        sys.stderr.write(f"Publication failed: {failure}\n")
        return 1
    assert result is not None
    sys.stdout.write(f"Published: {result.output}\n")
    return 0
