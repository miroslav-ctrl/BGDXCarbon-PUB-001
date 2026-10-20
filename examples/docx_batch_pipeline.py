"""Installed-wheel batch DOCX contracts and two distinct visual samples."""

import logging
import sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from docx import Document

import bgdxpublisher
from bgdxpublisher.docx_batch_pipeline import (
    BatchDocxPublicationError,
    BatchDocxPublicationService,
    BatchDocxRequest,
)
from bgdxpublisher.docx_pipeline import DocxPublicationService
from bgdxpublisher.publishing.docx import DocxRequest
from bgdxpublisher.runtime import PublisherApplication


def verify(root: Path) -> None:
    """Verify installed imports, exact OOXML, outcomes and retained refusal bytes."""
    assert "site-packages" in Path(bgdxpublisher.__file__).parts
    root.mkdir(parents=True, exist_ok=True)
    source = root / "sources"
    source.mkdir()
    (source / "report.md").write_text(
        "# Čć Ћирилица\n\n**Bold report** with *emphasis*.\n\n"
        "## Findings\n\n- First item\n- Second item\n\n"
        "[Reference](https://example.com)\n",
        encoding="utf-8-sig",
    )
    (source / "notes.MD").write_text(
        "# Beleške / Белешке\n\n> Independent document and quote.\n\n"
        "3. Third step\n4. Fourth step\n\n`Code sample`\n",
        encoding="utf-8",
    )
    originals = {p: p.read_bytes() for p in source.iterdir()}
    app = PublisherApplication()
    app.initialize()
    app.start()
    try:
        service = app.context.services.resolve(BatchDocxPublicationService)
        single = app.context.services.resolve(DocxPublicationService)
        request = BatchDocxRequest(source, root / "published", language="sr-Latn")
        result = service.publish(request)
        assert (result.success_count, result.failure_count) == (2, 0)
        assert [p.source.name for p in result.items] == ["notes.MD", "report.md"]
        individual = root / "individual"
        individual.mkdir()
        for item in result.items:
            document = Document(item.output)
            assert document.core_properties.title == item.source.stem
            assert document.core_properties.language == "sr-Latn"
            assert item.execution.pipeline_result.output.output == item.output
            target = individual / item.output.name
            single.publish(DocxRequest(item.source, target, language="sr-Latn"))
            with ZipFile(target) as expected, ZipFile(item.output) as actual:
                assert set(actual.namelist()) == set(expected.namelist())
                assert all(
                    actual.read(n) == expected.read(n) for n in actual.namelist()
                )
        before = {p.output: p.output.read_bytes() for p in result.items}
        failed = service.publish(request)
        assert (failed.success_count, failed.failure_count) == (0, 2)
        assert all(
            p.execution.pipeline_result.failure.stage_name == "validate"
            for p in failed.items
        )
        assert all(p.read_bytes() == b for p, b in before.items())
        (request.output_dir / "report.docx").unlink()
        mixed = service.publish(request)
        assert (mixed.success_count, mixed.failure_count) == (1, 1)
        again = service.publish(replace(request, overwrite=True))
        assert again.success_count == 2
        assert not {p.execution.final_job.job_id for p in result.items}.intersection(
            p.execution.final_job.job_id for p in again.items
        )
        try:
            service.publish(replace(request, language="en_US"))
        except BatchDocxPublicationError as error:
            assert str(error) == "BATCH_DOCX_PREFLIGHT_FAILED" and error.__cause__
        else:
            raise AssertionError("invalid language accepted")
        assert all(p.read_bytes() == b for p, b in originals.items())
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
