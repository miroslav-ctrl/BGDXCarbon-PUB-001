"""Verify installed batch PDF API; optional directory retains single/multipage PDFs."""

import logging
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

import bgdxpublisher
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.pdf_batch_pipeline import (
    BatchPdfPublicationError,
    BatchPdfPublicationService,
    BatchPdfRequest,
)
from bgdxpublisher.pdf_pipeline import PdfPublicationService
from bgdxpublisher.publishing.pdf import PdfRequest
from bgdxpublisher.runtime import PublisherApplication


def verify(root: Path) -> None:
    """Exercise runtime-only installed imports and independent terminal outcomes."""
    assert "site-packages" in Path(bgdxpublisher.__file__).parts
    root.mkdir(parents=True, exist_ok=True)
    source = root / "sources"
    source.mkdir()
    (source / "sample.md").write_text(
        "# Izveštaj / Ћирилица\n\nČćžšđ **bold** *italic* `code`.\n\n"
        "- First\n  - Nested\n\n3. Third\n4. Fourth\n\n> Quote\n\n"
        "[safe](https://example.com) ![alt](https://example.com/image)\n\n"
        "```python\nprint('Здраво')\n```",
        encoding="utf-8-sig",
    )
    (source / "multipage.MD").write_text(
        "# Multipage / Ћирилица\n\n"
        + "Paragraph Čć text.\n\n" * 65
        + "## Steps\n\n3. Third\n4. Fourth\n\n"
        + "```python\n"
        + "print('Здраво')\n" * 25
        + "```",
        encoding="utf-8",
    )
    before = {p: p.read_bytes() for p in source.iterdir()}
    config = root / "config.yaml"
    config.write_text(
        "app:\n  name: Test\n  version: 1.1.0\n"
        "logging:\n  level: CRITICAL\n  console: false\n",
        encoding="utf-8",
    )
    app = PublisherApplication(config_path=config)
    app.initialize()
    app.start()
    try:
        service = app.context.services.resolve(BatchPdfPublicationService)
        single = app.context.services.resolve(PdfPublicationService)
        request = BatchPdfRequest(source, root / "published", language="sr-Latn")
        result = service.publish(request)
        assert (result.success_count, result.failure_count) == (2, 0)
        assert [p.source.name for p in result.items] == ["multipage.MD", "sample.md"]
        assert all(
            p.execution.final_job.status is JobStatus.COMPLETED for p in result.items
        )
        assert all(p.output.read_bytes().startswith(b"%PDF-") for p in result.items)
        original = {p.output: p.output.read_bytes() for p in result.items}
        failed = service.publish(request)
        assert (failed.success_count, failed.failure_count) == (0, 2)
        assert all(
            p.execution.pipeline_result.failure.stage_name == "validate"
            for p in failed.items
        )
        assert all(p.read_bytes() == b for p, b in original.items())
        (request.output_dir / "sample.pdf").unlink()
        mixed = service.publish(request)
        assert (mixed.success_count, mixed.failure_count) == (1, 1)
        (source / "multipage.MD").write_text("Unsupported 漢 SECRET", encoding="utf-8")
        glyph = service.publish(replace(request, overwrite=True))
        assert (glyph.success_count, glyph.failure_count) == (1, 1)
        assert glyph.items[0].execution.pipeline_result.failure.stage_name == "render"
        assert glyph.items[0].execution.pipeline_result.output is None
        assert glyph.items[1].execution.final_job.status is JobStatus.COMPLETED
        (source / "multipage.MD").write_bytes(b"\xff")
        encoding = service.publish(replace(request, overwrite=True))
        assert encoding.items[0].execution.pipeline_result.failure.stage_name == "read"
        (source / "multipage.MD").write_bytes(before[source / "multipage.MD"])
        for bad in (
            replace(request, language="en_US"),
            replace(request, source_dir=root / "missing"),
        ):
            try:
                service.publish(bad)
            except BatchPdfPublicationError as error:
                assert str(error) == error.code == "BATCH_PDF_PREFLIGHT_FAILED"
                assert error.__cause__ is not None
            else:
                raise AssertionError("invalid batch accepted")
        again = service.publish(replace(request, overwrite=True))
        assert again.success_count == 2
        assert not {p.execution.final_job.job_id for p in result.items}.intersection(
            p.execution.final_job.job_id for p in again.items
        )
        individual = root / "individual"
        individual.mkdir()
        for item in again.items:
            direct = single.publish(
                PdfRequest(
                    item.source,
                    individual / item.output.name,
                    language=request.language,
                )
            )
            assert direct.publication.bytes_written == len(
                direct.publication.output.read_bytes()
            )
            assert item.execution.pipeline_result.output.output == item.output
            assert item.execution.pipeline_result.output.bytes_written == len(
                item.output.read_bytes()
            )
        assert all(p.read_bytes() == b for p, b in before.items())
        assert not list(request.output_dir.glob(".bgdx-*.tmp"))
    finally:
        app.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    if len(sys.argv) > 1:
        verify(Path(sys.argv[1]).resolve())
    else:
        with TemporaryDirectory() as directory:
            verify(Path(directory))
