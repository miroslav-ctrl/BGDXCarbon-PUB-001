"""Exercise the installed PDF pipeline API; optional directory retains previews."""

import logging
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import bgdxpublisher
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.pdf_pipeline import PdfPublicationError, PdfPublicationService
from bgdxpublisher.publishing.pdf import PdfRequest
from bgdxpublisher.runtime import PublisherApplication


def verify(root: Path, sample: Path | None = None) -> None:
    """Validate installed API outcomes and create single/multipage examples."""
    assert "site-packages" in Path(bgdxpublisher.__file__).parts
    root.mkdir(parents=True, exist_ok=True)
    source = root / "sample.md"
    source.write_text(
        "# Izveštaj / Ћирилица\n\nČćžšđ **bold** *italic* `code`.\n\n"
        "- First\n  - Nested\n\n3. Third\n4. Fourth\n\n"
        "Separate:\n\n1. Restart\n2. Second\n\n> Quote\n\n"
        "[safe](https://example.com) ![alt](https://example.com/image)\n\n"
        "```python\nprint('Zdravo / Здраво')\n```",
        encoding="utf-8-sig",
    )
    if sample is not None:
        source.write_bytes(sample.read_bytes())
    original = source.read_bytes()
    request = PdfRequest(
        source, root / "sample.pdf", title="Izveštaj", language="sr-Latn"
    )
    app = PublisherApplication()
    app.initialize()
    app.start()
    try:
        service = app.context.services.resolve(PdfPublicationService)
        result = service.publish(request)
        assert result.execution.final_job.status is JobStatus.COMPLETED
        assert result.publication.bytes_written == len(request.output.read_bytes())
        assert request.output.read_bytes().startswith(b"%PDF-")
        previous = request.output.read_bytes()
        try:
            service.publish(request)
        except PdfPublicationError as error:
            assert str(error) == "PDF_PUBLICATION_FAILED"
            assert error.result.pipeline_result.failure.stage_name == "validate"
        else:
            raise AssertionError("overwrite must be explicit")
        assert request.output.read_bytes() == previous
        again = service.publish(replace(request, overwrite=True))
        assert again.execution.final_job.job_id != result.execution.final_job.job_id
        previous = request.output.read_bytes()
        source.write_bytes(b"\xff")
        try:
            service.publish(replace(request, overwrite=True))
        except PdfPublicationError as error:
            assert str(error) == "PDF_PUBLICATION_FAILED"
            assert error.result.pipeline_result.failure.stage_name == "read"
            assert error.result.pipeline_result.output is None
        else:
            raise AssertionError("invalid UTF-8 must fail")
        assert request.output.read_bytes() == previous
        assert not list(root.glob(".bgdx-*.tmp"))
        source.write_bytes(original)
        long_source = root / "multipage.md"
        long_source.write_text(
            "# Multipage / Ћирилица\n\n"
            + "Paragraph Čć text.\n\n" * 90
            + "```python\n"
            + "print('Здраво')\n" * 70
            + "```",
            encoding="utf-8",
        )
        service.publish(
            replace(request, source=long_source, output=root / "multipage.pdf")
        )
        assert source.read_bytes() == original
    finally:
        app.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    if len(sys.argv) > 1:
        verify(
            Path(sys.argv[1]).resolve(),
            Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None,
        )
    else:
        with TemporaryDirectory() as directory:
            verify(Path(directory))
