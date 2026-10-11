"""CLI adapter for batch publication."""

import sys
from pathlib import Path

from bgdxpublisher.publishing import PublishingService
from bgdxpublisher.publishing.batch import BatchRequest, publish_batch
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


def run_batch(
    source: Path,
    output: Path,
    overwrite: bool,
    config: Path | None,
    language: str,
    theme: str,
    toc: bool,
    index: bool = False,
) -> int:
    """Use one runtime and report every completed attempt."""
    application = PublisherApplication(config_path=config)
    failed = False
    try:
        application.initialize()
        application.start()
        results = publish_batch(
            application.context.services.resolve(PublishingService),
            BatchRequest(source, output, overwrite, language, theme, toc, index),
        )
        for item in results.items:
            if item.error is not None:
                sys.stderr.write(f"Failed: {item.source}: {item.error}\n")
            else:
                sys.stdout.write(f"Published: {item.output}\n")
        failures = sum(item.error is not None for item in results.items)
        sys.stdout.write(
            f"Batch complete: {len(results.items) - failures} published, "
            f"{failures} failed.\n"
        )
        if results.index is not None:
            sys.stdout.write(f"Index published: {results.index.output}\n")
        if results.index_error is not None:
            sys.stderr.write(f"Index publication failed: {results.index_error}\n")
        failed = failures > 0 or results.index_error is not None
    except RuntimeFoundationError as error:
        sys.stderr.write(f"Batch publication failed: {error}\n")
        failed = True
    finally:
        if application.state in (RuntimeState.CONFIGURED, RuntimeState.RUNNING):
            try:
                application.stop()
            except RuntimeFoundationError as error:
                sys.stderr.write(f"Runtime cleanup failed: {error}\n")
                failed = True
    return int(failed)
