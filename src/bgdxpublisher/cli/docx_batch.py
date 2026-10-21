"""CLI projection of independent DOCX batch outcomes."""

import sys
from pathlib import Path

from bgdxpublisher.docx_batch_pipeline import (
    BatchDocxPublicationError,
    BatchDocxPublicationService,
    BatchDocxRequest,
)
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


def run_docx_batch(
    source: Path,
    output: Path,
    overwrite: bool,
    config: Path | None,
    language: str,
) -> int:
    """Report terminal outcomes only after one runtime has closed successfully."""
    application = PublisherApplication(config_path=config)
    stdout: list[str] = []
    failed = False
    shutdown_failed = False
    try:
        application.initialize()
        application.start()
        result = application.context.services.resolve(
            BatchDocxPublicationService
        ).publish(BatchDocxRequest(source, output, overwrite, language))
        for ordinal, item in enumerate(result.items, start=1):
            if item.execution.final_job.status is JobStatus.FAILED:
                detail = item.execution.pipeline_result.failure
                assert detail is not None
                sys.stderr.write(
                    f"Failed: item={ordinal} DOCX_PUBLICATION_FAILED "
                    f"stage={detail.stage_name}\n"
                )
            else:
                stdout.append(f"Published: {item.output}\n")
        stdout.append(
            f"Batch complete: {result.success_count} published, "
            f"{result.failure_count} failed.\n"
        )
        failed = result.failure_count > 0
    except BatchDocxPublicationError:
        sys.stderr.write("Batch publication failed: BATCH_DOCX_PREFLIGHT_FAILED\n")
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
