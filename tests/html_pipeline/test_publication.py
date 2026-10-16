"""HTML pipeline compatibility, failure boundaries and runtime tests."""

import logging
import os
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from bgdxpublisher.html_pipeline import (
    HtmlPublicationError,
    HtmlPublicationResult,
    HtmlPublicationService,
)
from bgdxpublisher.html_pipeline.service import ReadStage, RenderStage, WriteStage
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.orchestration import JobExecutionError, JobExecutionService
from bgdxpublisher.pipeline import PipelineEngine, PipelineExecutionError
from bgdxpublisher.publishing import PublishingService, PublishRequest
from bgdxpublisher.runtime import PublisherApplication


def setup(tmp_path):
    source = tmp_path / "source.md"
    source.write_text(
        "# Naslov\n\nČćžšđ Ћирилица.\n\n## Podnaslov", encoding="utf-8-sig"
    )
    return PublishRequest(source, tmp_path / "out.html")


def service():
    return HtmlPublicationService(logging.getLogger("test.html_pipeline"))


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("toc", [True, False])
@pytest.mark.parametrize(
    "title,language", [(None, "und"), ("Čć & <naslov>", "sr-Latn")]
)
def test_equivalence(tmp_path, theme, toc, title, language):
    request = replace(
        setup(tmp_path), theme=theme, toc=toc, title=title, language=language
    )
    before = request.source.read_bytes()
    result = service().publish(request)
    legacy = replace(request, output=tmp_path / "legacy.html")
    PublishingService(logging.getLogger("legacy")).publish(legacy)
    assert request.output.read_bytes() == legacy.output.read_bytes()
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
        HtmlPublicationError(result.execution)


@pytest.mark.parametrize(
    "option,value", [("title", ""), ("language", "en_US"), ("theme", "invalid")]
)
def test_invalid_metadata_preserves_files(tmp_path, option, value):
    request = setup(tmp_path)
    request.output.write_bytes(b"old")
    before = request.source.read_bytes()
    with pytest.raises(HtmlPublicationError) as error:
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
    ],
)
def test_invalid_paths(tmp_path, mode):
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
        request = replace(request, output=tmp_path / "missing" / "out")
    else:
        request.output.mkdir()
    with pytest.raises(HtmlPublicationError) as error:
        service().publish(request)
    assert error.value.result.final_job.status is JobStatus.FAILED


def test_output_symlink(tmp_path):
    request = setup(tmp_path)
    try:
        request.output.symlink_to(request.source)
    except OSError:
        pytest.skip("Symlink permission unavailable")
    with pytest.raises(HtmlPublicationError):
        service().publish(replace(request, overwrite=True))


@pytest.mark.parametrize("stage", [ReadStage, RenderStage, WriteStage])
def test_stage_failure_chain_and_safe_logs(tmp_path, monkeypatch, caplog, stage):
    request = setup(tmp_path)
    request.output.write_bytes(b"old")

    def fail(*args):
        raise OSError("secret-sentinel")

    monkeypatch.setattr(stage, "execute", fail)
    caplog.set_level(logging.INFO, logger="test.html_pipeline")
    with pytest.raises(HtmlPublicationError) as error:
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
        HtmlPublicationResult(None, error.value.result)


def test_encoding_failure(tmp_path):
    request = setup(tmp_path)
    request.source.write_bytes(b"\xff")
    with pytest.raises(HtmlPublicationError) as error:
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
    with pytest.raises(HtmlPublicationError):
        service().publish(request)
    assert request.output.read_bytes() == b"competitor"
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


def test_precommit_write_failure_and_cleanup(tmp_path, monkeypatch):
    request = setup(tmp_path)
    request.output.write_bytes(b"old")

    def fail(*args):
        raise OSError("commit failed")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(HtmlPublicationError):
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
        with pytest.raises(HtmlPublicationError) as error:
            publisher.publish(replace(request, overwrite=True))
        assert error.value.result.pipeline_result.failure.stage_name == "cleanup"
        assert error.value.result.pipeline_result.output is None
        assert request.output.read_bytes().startswith(b"<!doctype html>")
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
        app.context.services.resolve(HtmlPublicationService).publish(request)
        assert calls == ["read", "render", "write"]
        from uuid import uuid4

        from bgdxpublisher.jobs import JobStatus, PublisherJob

        job = PublisherJob(document_id=str(uuid4()), status=JobStatus.QUEUED)
        result = app.context.services.resolve(JobExecutionService).execute(job, 1)
        assert result.pipeline_result.output == 1
        assert isinstance(app.context.services.resolve(PipelineEngine), PipelineEngine)
    finally:
        app.stop()
