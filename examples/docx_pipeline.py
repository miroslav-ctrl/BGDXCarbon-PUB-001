"""Installed-wheel DOCX pipeline API verification alongside the legacy CLI."""

import logging
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from docx import Document

import bgdxpublisher
from bgdxpublisher.docx_pipeline import DocxPublicationError, DocxPublicationService
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.publishing.docx import DocxPublishingService, DocxRequest
from bgdxpublisher.runtime import PublisherApplication


def main() -> None:
    """Verify installed imports, OOXML content and independent executions."""
    assert "site-packages" in Path(bgdxpublisher.__file__).parts
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source, output = root / "sample.md", root / "sample.docx"
        source.write_text(
            "# Čć Ћирилица\n\n**Bold** *italic* `code`\n\n"
            "- First\n- Second\n\n3. Third\n\n> Quote\n\n"
            "[link](https://example.com) ![alt](https://example.com/image)",
            encoding="utf-8-sig",
        )
        original_source = source.read_bytes()
        app = PublisherApplication()
        app.initialize()
        app.start()
        try:
            service = app.context.services.resolve(DocxPublicationService)
            request = DocxRequest(source, output, title="Izveštaj", language="sr-Latn")
            result = service.publish(request)
            assert result.execution.final_job.status is JobStatus.COMPLETED
            assert result.publication.bytes_written == len(output.read_bytes())
            document = Document(output)
            assert document.core_properties.title == "Izveštaj"
            assert document.core_properties.language == "sr-Latn"
            assert document.paragraphs[0].text == "Čć Ћирилица"
            legacy = root / "legacy.docx"
            app.context.services.resolve(DocxPublishingService).publish(
                replace(request, output=legacy)
            )
            with ZipFile(output) as actual, ZipFile(legacy) as expected:
                assert set(actual.namelist()) == set(expected.namelist())
                assert all(
                    actual.read(p) == expected.read(p) for p in actual.namelist()
                )
            previous = output.read_bytes()
            try:
                service.publish(request)
            except DocxPublicationError as error:
                assert error.code == "DOCX_PUBLICATION_FAILED"
                assert error.result.pipeline_result.failure.stage_name == "validate"
            else:
                raise AssertionError("overwrite must be explicit")
            assert output.read_bytes() == previous
            again = service.publish(replace(request, overwrite=True))
            assert again.execution.final_job.job_id != result.execution.final_job.job_id
            source.write_bytes(b"\xff")
            before = output.read_bytes()
            try:
                service.publish(replace(request, overwrite=True))
            except DocxPublicationError as error:
                assert error.result.pipeline_result.failure.stage_name == "read"
                assert error.result.pipeline_result.output is None
            else:
                raise AssertionError("invalid UTF-8 must fail")
            assert output.read_bytes() == before
            assert not list(root.glob(".bgdx-*.tmp"))
            source.write_bytes(original_source)
        finally:
            app.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    main()
