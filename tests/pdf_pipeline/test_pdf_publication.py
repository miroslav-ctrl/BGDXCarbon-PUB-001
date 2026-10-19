"""PDF pipeline compatibility, failure boundaries and runtime tests."""

import logging
import os
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.orchestration import JobExecutionError, JobExecutionService
from bgdxpublisher.pdf_pipeline import (
    PdfPublicationError,
    PdfPublicationResult,
    PdfPublicationService,
)
from bgdxpublisher.pdf_pipeline.service import ReadStage, RenderStage, WriteStage
from bgdxpublisher.pipeline import PipelineEngine, PipelineExecutionError
from bgdxpublisher.publishing import PublishResult
from bgdxpublisher.publishing.pdf import PdfPublishingService, PdfRequest
from bgdxpublisher.runtime import PublisherApplication


def setup(tmp_path):
    source = tmp_path / "source.md"
    source.write_text(
        "# Naslov\n\nČćžšđ Ћирилица.\n\n## Podnaslov", encoding="utf-8-sig"
    )
    return PdfRequest(source, tmp_path / "out.pdf")


def service():
    return PdfPublicationService(logging.getLogger("test.pdf_pipeline"))


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
@pytest.mark.parametrize("custom", [False, True])
@pytest.mark.parametrize(
    "text",
    [
        "",
        "# Naslov Ћирилица\n\n**bold** *italic* `code`\n\n"
        "- first\n  - nested\n\n3. third\n\n> quote\n\n"
        "```python\nprint(1)\n```\n\n[safe](https://example.com) "
        "![alt](https://example.com/image) <script>x</script>",
        (
            "# Page Ћирилица\n\n"
            + "Paragraph Čć text.\n\n" * 90
            + "```python\n"
            + "print(1)\n" * 70
            + "```"
        ),
    ],
)
def test_equivalence(tmp_path, encoding, custom, text):
    from pypdf import PdfReader

    request = replace(
        setup(tmp_path),
        title="Čć & <naslov>" if custom else None,
        language="sr-Latn" if custom else "und",
    )
    request.source.write_text(text, encoding=encoding)
    before = request.source.read_bytes()
    result = service().publish(request)
    legacy = replace(request, output=tmp_path / "legacy.pdf")
    PdfPublishingService(logging.getLogger("legacy")).publish(legacy)
    actual, expected = PdfReader(request.output), PdfReader(legacy.output)
    assert (
        actual.metadata.title
        == expected.metadata.title
        == (request.title or request.source.stem)
    )
    assert (
        actual.trailer["/Root"]["/Lang"]
        == expected.trailer["/Root"]["/Lang"]
        == request.language
    )
    assert len(actual.pages) == len(expected.pages)
    for page, other in zip(actual.pages, expected.pages):
        assert list(page.mediabox) == list(other.mediabox)
        assert float(page.mediabox.width) == pytest.approx(595.276, abs=0.01)
        assert float(page.mediabox.height) == pytest.approx(841.89, abs=0.01)
        assert page.extract_text() == other.extract_text()
        assert page.get_contents().get_data() == other.get_contents().get_data()

        def links(value):
            return [
                (
                    list(a.get_object()["/Rect"]),
                    str(a.get_object().get("/A", {}).get("/URI", "")),
                )
                for a in value.get("/Annots", [])
            ]

        assert links(page) == links(other)

        def fonts(value):
            result = []
            for item in value["/Resources"]["/Font"].values():
                font = item.get_object()
                descriptor = font.get("/FontDescriptor")
                embedded = (
                    descriptor is not None and "/FontFile2" in descriptor.get_object()
                )
                result.append((str(font["/BaseFont"]), embedded))
            return sorted(result)

        assert fonts(page) == fonts(other)
        if page.extract_text().strip():
            assert any(embedded for _, embedded in fonts(page))
    assert result.publication.bytes_written == len(request.output.read_bytes())
    assert request.source.read_bytes() == before
    assert result.execution.pipeline_result.completed_stages == (
        "validate",
        "read",
        "render",
        "write",
    )
    assert result.execution.status_history == (
        JobStatus.QUEUED,
        JobStatus.RUNNING,
        JobStatus.COMPLETED,
    )
    with pytest.raises(FrozenInstanceError):
        result.publication = None
    with pytest.raises(ValueError):
        replace(result, publication=replace(result.publication, bytes_written=0))
    with pytest.raises(ValueError):
        PdfPublicationError(result.execution)


@pytest.mark.parametrize("option,value", [("title", ""), ("language", "en_US")])
def test_invalid_metadata_preserves_files(tmp_path, monkeypatch, option, value):
    request = setup(tmp_path)
    request.output.write_bytes(b"old")
    before = request.source.read_bytes()

    def forbidden(*args):
        pytest.fail("read before validation")

    monkeypatch.setattr(ReadStage, "execute", forbidden)
    with pytest.raises(PdfPublicationError) as error:
        service().publish(replace(request, overwrite=True, **{option: value}))
    assert error.value.result.pipeline_result.failure.stage_name == "validate"
    assert request.output.read_bytes() == b"old"
    assert request.source.read_bytes() == before


@pytest.mark.parametrize(
    "mode",
    [
        "missing",
        "directory",
        "alias",
        "hardlink",
        "exists",
        "parent",
        "output-directory",
        "extension",
    ],
)
def test_invalid_paths(tmp_path, monkeypatch, mode):
    request = setup(tmp_path)
    if mode == "missing":
        request = replace(request, source=tmp_path / "missing")
    elif mode == "directory":
        request = replace(request, source=tmp_path)
    elif mode == "alias":
        request = replace(request, output=request.source)
    elif mode == "hardlink":
        os.link(request.source, request.output)
    elif mode == "exists":
        request.output.write_bytes(b"old")
    elif mode == "parent":
        request = replace(request, output=tmp_path / "missing" / "out.pdf")
    elif mode == "extension":
        request = replace(request, output=tmp_path / "wrong.html")
    else:
        request.output.mkdir()

    def forbidden(*args):
        pytest.fail("read before validation")

    monkeypatch.setattr(ReadStage, "execute", forbidden)
    with pytest.raises(PdfPublicationError) as error:
        service().publish(request)
    assert error.value.result.final_job.status is JobStatus.FAILED
    assert error.value.result.pipeline_result.failure.stage_name == "validate"


def test_output_symlink(tmp_path):
    request = setup(tmp_path)
    try:
        request.output.symlink_to(request.source)
    except OSError:
        pytest.skip("Symlink permission unavailable")
    with pytest.raises(PdfPublicationError):
        service().publish(replace(request, overwrite=True))


@pytest.mark.parametrize("stage", [ReadStage, RenderStage, WriteStage])
def test_stage_failure_chain_and_safe_logs(tmp_path, monkeypatch, caplog, stage):
    request = setup(tmp_path)
    request.output.write_bytes(b"old")

    def fail(*args):
        raise OSError("secret-sentinel")

    monkeypatch.setattr(stage, "execute", fail)
    caplog.set_level(logging.INFO, logger="test.pdf_pipeline")
    with pytest.raises(PdfPublicationError) as error:
        service().publish(replace(request, overwrite=True))
    assert isinstance(error.value.__cause__, JobExecutionError)
    assert isinstance(error.value.__cause__.__cause__, PipelineExecutionError)
    assert isinstance(error.value.__cause__.__cause__.__cause__, OSError)
    assert error.value.result.pipeline_result.output is None
    assert error.value.result.pipeline_result.failure.stage_name == stage.name
    assert request.output.read_bytes() == b"old"
    assert "secret-sentinel" not in caplog.text
    assert str(request.source) not in caplog.text
    assert "Ћирилица" not in caplog.text
    with pytest.raises(ValueError):
        PdfPublicationResult(PublishResult(request.output, 0), error.value.result)


def test_encoding_failure(tmp_path):
    request = setup(tmp_path)
    request.source.write_bytes(b"\xff")
    with pytest.raises(PdfPublicationError) as error:
        service().publish(request)
    assert error.value.result.pipeline_result.failure.stage_name == "read"
    assert not request.output.exists()


def test_no_overwrite_race_and_cleanup(tmp_path, monkeypatch):
    request = setup(tmp_path)
    original = os.link

    def race(source, output):
        Path(output).write_bytes(b"competitor")
        return original(source, output)

    monkeypatch.setattr(os, "link", race)
    with pytest.raises(PdfPublicationError):
        service().publish(request)
    assert request.output.read_bytes() == b"competitor"
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


def test_precommit_write_failure_and_cleanup(tmp_path, monkeypatch):
    request = setup(tmp_path)
    request.output.write_bytes(b"old")

    def fail(*args):
        raise OSError("commit failed")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(PdfPublicationError):
        service().publish(replace(request, overwrite=True))
    assert request.output.read_bytes() == b"old"
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


def test_postcommit_cleanup_and_context_isolation(tmp_path, monkeypatch):
    request = setup(tmp_path)
    original = WriteStage.execute
    contexts = []
    calls = []

    def execute(self, value, context):
        contexts.append(context)

        def cleanup():
            calls.append("cleanup")
            raise OSError("cleanup failed")

        context.register_cleanup(cleanup)
        return original(self, value, context)

    monkeypatch.setattr(WriteStage, "execute", execute)
    publisher = service()
    for _ in range(2):
        with pytest.raises(PdfPublicationError) as error:
            publisher.publish(replace(request, overwrite=True))
        assert error.value.result.pipeline_result.failure.stage_name == "cleanup"
        assert error.value.result.pipeline_result.output is None
        assert request.output.read_bytes().startswith(b"%PDF-")
    assert contexts[0] is not contexts[1]
    assert contexts[0].job.job_id != contexts[1].job.job_id
    assert calls == ["cleanup", "cleanup"]


def test_runtime_and_single_operations(tmp_path, monkeypatch):
    request = setup(tmp_path)
    calls = []
    for stage in (ReadStage, RenderStage, WriteStage):
        original = stage.execute

        def execute(self, value, context, original=original):
            calls.append(self.name)
            return original(self, value, context)

        monkeypatch.setattr(stage, "execute", execute)
    app = PublisherApplication()
    app.initialize()
    app.start()
    try:
        app.context.services.resolve(PdfPublicationService).publish(request)
        assert calls == ["read", "render", "write"]
        from uuid import uuid4

        from bgdxpublisher.jobs import JobStatus, PublisherJob

        job = PublisherJob(document_id=str(uuid4()), status=JobStatus.QUEUED)
        result = app.context.services.resolve(JobExecutionService).execute(job, 1)
        assert result.pipeline_result.output == 1
        assert isinstance(app.context.services.resolve(PipelineEngine), PipelineEngine)
    finally:
        app.stop()


def test_legacy_direct_api_retains_contract(tmp_path, monkeypatch):
    from bgdxpublisher.publishing import PublishingError

    request = setup(tmp_path)

    def forbidden(*args):
        pytest.fail("legacy API must not redirect to pipeline")

    monkeypatch.setattr(PdfPublicationService, "publish", forbidden)
    publisher = PdfPublishingService(logging.getLogger("legacy-direct"))
    result = publisher.publish(request)
    assert result.output == request.output
    assert result.bytes_written == len(request.output.read_bytes())
    before = request.output.read_bytes()
    with pytest.raises(PublishingError, match="Output exists; use --overwrite"):
        publisher.publish(request)
    assert request.output.read_bytes() == before


def test_new_api_never_calls_legacy_and_has_fresh_ids(tmp_path, monkeypatch):
    from bgdxpublisher.pdf_pipeline.service import ValidateStage

    request = replace(setup(tmp_path), output=tmp_path / "UPPER.PDF", overwrite=True)
    original = ValidateStage.execute
    jobs = []

    def execute(self, value, context):
        jobs.append(context.job)
        return original(self, value, context)

    def forbidden(*args):
        pytest.fail("legacy PDF publish fallback")

    monkeypatch.setattr(ValidateStage, "execute", execute)
    monkeypatch.setattr(PdfPublishingService, "publish", forbidden)
    publisher = service()
    for _ in range(2):
        publisher.publish(request)
    assert jobs[0].job_id != jobs[1].job_id
    assert jobs[0].document_id != jobs[1].document_id


@pytest.mark.parametrize("failure", ["render", "flush"])
def test_real_stage_failure_preserves_bytes(tmp_path, monkeypatch, caplog, failure):
    from bgdxpublisher.publishing.pdf import PdfRenderer

    request = setup(tmp_path)
    request.output.write_bytes(b"previous")
    before = request.source.read_bytes()

    def fail(*args):
        raise ValueError("secret-raw-cause " + str(request.source))

    if failure == "render":
        monkeypatch.setattr(PdfRenderer, "render", fail)
    else:
        monkeypatch.setattr(os, "fsync", fail)
    caplog.set_level(logging.INFO, logger="test.pdf_pipeline")
    with pytest.raises(PdfPublicationError) as error:
        service().publish(replace(request, overwrite=True))
    assert error.value.result.pipeline_result.failure.stage_name == (
        "render" if failure == "render" else "write"
    )
    assert "secret-raw-cause" not in str(error.value) + caplog.text
    assert str(request.source) not in caplog.text
    assert request.output.read_bytes() == b"previous"
    assert request.source.read_bytes() == before
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


def test_cli_retains_legacy_route(tmp_path, monkeypatch, capsys):
    from bgdxpublisher.cli.app import main

    request = setup(tmp_path)
    calls = []
    original = PdfPublishingService.publish

    def publish(self, value):
        calls.append(value)
        return original(self, value)

    def forbidden(*args):
        pytest.fail("CLI must retain legacy PDF route")

    monkeypatch.setattr(PdfPublishingService, "publish", publish)
    monkeypatch.setattr(PdfPublicationService, "publish", forbidden)
    args = ["publish-pdf", str(request.source), "--output", str(request.output)]
    assert main(args) == 0
    assert calls == [request]
    assert capsys.readouterr().out == f"Published: {request.output}\n"
    assert main(args) == 1
    assert (
        capsys.readouterr().err
        == "Publication failed: Output exists; use --overwrite to replace it.\n"
    )


@pytest.mark.parametrize("kind", ["glyph", "control", "font", "layout"])
def test_render_failure_boundaries(tmp_path, monkeypatch, caplog, kind):
    from reportlab.pdfbase.ttfonts import TTFError
    from reportlab.platypus.doctemplate import LayoutError

    from bgdxpublisher.publishing import pdf

    request = replace(setup(tmp_path), title="secret-title", overwrite=True)
    request.output.write_bytes(b"previous")
    if kind in ("glyph", "control"):
        request.source.write_text(
            "secret-body " + ("\u4e00" if kind == "glyph" else "\x01"),
            encoding="utf-8",
        )
    else:

        def fail(*args, **kwargs):
            raise (TTFError if kind == "font" else LayoutError)("secret-cause")

        monkeypatch.setattr(
            pdf, "_register_fonts" if kind == "font" else "SimpleDocTemplate", fail
        )
    before = request.source.read_bytes()
    caplog.set_level(logging.INFO, logger="test.pdf_pipeline")
    with pytest.raises(PdfPublicationError) as error:
        service().publish(request)
    assert error.value.result.pipeline_result.failure.stage_name == "render"
    assert error.value.result.final_job.status is JobStatus.FAILED
    assert str(error.value) == "PDF_PUBLICATION_FAILED"
    assert error.value.__cause__.__cause__.__cause__ is not None
    for secret in (
        str(request.source),
        str(request.output),
        "secret-title",
        "secret-body",
        "secret-cause",
    ):
        assert secret not in caplog.text + str(error.value)
    assert request.output.read_bytes() == b"previous"
    assert request.source.read_bytes() == before


@pytest.mark.parametrize("fail", [False, True])
def test_caller_owns_runtime_shutdown(tmp_path, fail):
    from bgdxpublisher.runtime import RuntimeState

    app = PublisherApplication()
    app.initialize()
    app.start()
    request = setup(tmp_path)
    if fail:
        request.source.unlink()
    try:
        publisher = app.context.services.resolve(PdfPublicationService)
        if fail:
            with pytest.raises(PdfPublicationError):
                publisher.publish(request)
        else:
            publisher.publish(request)
        assert app.state is RuntimeState.RUNNING
    finally:
        app.stop()
    assert app.state is RuntimeState.STOPPED
