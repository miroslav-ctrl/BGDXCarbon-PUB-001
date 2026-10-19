"""CLI adapter for batch publication."""

import sys
from pathlib import Path

from bgdxpublisher.batch_pipeline import (
    BatchHtmlPublicationError,
    BatchHtmlPublicationService,
)
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.publishing.batch import BatchRequest
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
    stdout: list[str] = []
    shutdown_failed = False
    try:
        application.initialize()
        application.start()
        results = application.context.services.resolve(
            BatchHtmlPublicationService
        ).publish(BatchRequest(source, output, overwrite, language, theme, toc, index))
        failures = 0
        for ordinal, item in enumerate(results.items, start=1):
            if item.execution.final_job.status is JobStatus.FAILED:
                failures += 1
                detail = item.execution.pipeline_result.failure
                assert detail is not None
                sys.stderr.write(
                    f"Failed: item={ordinal} HTML_PUBLICATION_FAILED "
                    f"stage={detail.stage_name}\n"
                )
            else:
                stdout.append(f"Published: {item.output}\n")
        stdout.append(
            f"Batch complete: {len(results.items) - failures} published, "
            f"{failures} failed.\n"
        )
        if results.index is not None:
            stdout.append(f"Index published: {results.index.output}\n")
        if results.index_failure is not None:
            sys.stderr.write("Index publication failed: BATCH_INDEX_FAILED\n")
        failed = failures > 0 or results.index_failure is not None
    except BatchHtmlPublicationError as error:
        sys.stderr.write(f"Batch publication failed: {error.code}\n")
        failed = True
    except RuntimeFoundationError as error:
        sys.stderr.write(f"Batch publication failed: {error}\n")
        failed = True
    finally:
        if application.state in (RuntimeState.CONFIGURED, RuntimeState.RUNNING):
            primary = sys.exception()
            try:
                application.stop()
            except Exception as error:
                if isinstance(error, RuntimeFoundationError):
                    sys.stderr.write(f"Runtime cleanup failed: {error}\n")
                    failed = True
                    shutdown_failed = True
                elif primary is None:
                    raise
                else:
                    primary.add_note("An unexpected runtime cleanup failure occurred.")
    if not shutdown_failed:
        sys.stdout.write("".join(stdout))
    return int(failed)
