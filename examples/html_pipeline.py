"""Publish HTML through the job pipeline using an installed package."""

import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from bgdxpublisher.html_pipeline import HtmlPublicationError, HtmlPublicationService
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.publishing import PublishingService, PublishRequest


def main() -> None:
    """Exercise byte-equivalence, overwrite refusal and invalid metadata."""
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "sample.md"
        source.write_text("# Izveštaj\n\nČćžšđ Ћирилица.", encoding="utf-8-sig")
        before = source.read_bytes()
        logger = logging.getLogger("html-pipeline-example")
        service = HtmlPublicationService(logger)
        request = PublishRequest(
            source,
            root / "pipeline.html",
            title="Izveštaj",
            language="sr-Latn",
            theme="dark",
            toc=True,
        )
        result = service.publish(request)
        assert result.execution.final_job.status is JobStatus.COMPLETED
        assert result.publication.bytes_written == len(request.output.read_bytes())
        legacy = PublishRequest(
            source,
            root / "legacy.html",
            title="Izveštaj",
            language="sr-Latn",
            theme="dark",
            toc=True,
        )
        PublishingService(logger).publish(legacy)
        assert request.output.read_bytes() == legacy.output.read_bytes()
        saved = request.output.read_bytes()
        for invalid in (
            request,
            PublishRequest(source, request.output, True, language="en_US"),
        ):
            try:
                service.publish(invalid)
            except HtmlPublicationError as error:
                assert error.result.final_job.status is JobStatus.FAILED
                assert error.result.pipeline_result.output is None
                assert error.__cause__ is not None
            else:
                raise AssertionError("Expected typed publication failure")
        assert request.output.read_bytes() == saved
        assert source.read_bytes() == before


if __name__ == "__main__":
    main()
