"""Batch compatibility, typed failures and independent index commits."""

import logging
import os
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from bgdxpublisher.batch_pipeline import (
    BatchHtmlPublicationError,
    BatchHtmlPublicationResult,
    BatchHtmlPublicationService,
)
from bgdxpublisher.html_pipeline import HtmlPublicationService
from bgdxpublisher.html_pipeline.service import WriteStage
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.publishing import PublishingService
from bgdxpublisher.publishing.batch import BatchRequest, publish_batch
from bgdxpublisher.runtime import PublisherApplication


def request(tmp_path, **kwargs):
    source = tmp_path / "sources"
    source.mkdir()
    (source / "b.MD").write_text("# Čć\n\nЋирилица.", encoding="utf-8-sig")
    (source / "A.md").write_text("# A\n\n## Heading", encoding="utf-8")
    (source / "ignore.txt").write_text("ignored")
    (source / "nested").mkdir()
    (source / "nested" / "nested.md").write_text("nested")
    return BatchRequest(source, tmp_path / "output", **kwargs)


def service(publisher=None):
    return BatchHtmlPublicationService(
        logging.getLogger("test.batch_pipeline"), publisher
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("toc", [False, True])
@pytest.mark.parametrize("index", [False, True])
def test_equivalence_and_invariants(tmp_path, theme, toc, index):
    req = request(tmp_path, theme=theme, toc=toc, index=index, language="sr-Latn")
    before = {p: p.read_bytes() for p in req.source_dir.iterdir() if p.is_file()}
    result = service().publish(req)
    legacy = replace(req, output_dir=tmp_path / "legacy")
    publish_batch(PublishingService(logging.getLogger("legacy")), legacy)
    assert [p.source.name for p in result.items] == ["A.md", "b.MD"]
    for p in result.items:
        assert p.execution.final_job.status is JobStatus.COMPLETED
        assert p.output.read_bytes() == (legacy.output_dir / p.output.name).read_bytes()
    assert len({p.execution.final_job.job_id for p in result.items}) == 2
    assert all(p.read_bytes() == content for p, content in before.items())
    if index:
        assert (
            result.index.output.read_bytes()
            == (legacy.output_dir / "index.html").read_bytes()
        )
    with pytest.raises(FrozenInstanceError):
        result.items = ()
    with pytest.raises(ValueError):
        replace(result, index_requested=not index)
    with pytest.raises(ValueError):
        replace(result.items[0], output=tmp_path / "wrong")
    with pytest.raises(ValueError):
        BatchHtmlPublicationResult((), True)


@pytest.mark.parametrize(
    "mode",
    [
        "language",
        "theme",
        "missing",
        "file",
        "empty",
        "collision",
        "index",
        "index-exists",
        "index-alias",
        "output-file",
    ],
)
def test_preflight_before_publication(tmp_path, monkeypatch, mode):
    req = request(tmp_path, index=True)
    if mode == "language":
        req = replace(req, language="en_US")
    elif mode == "theme":
        req = replace(req, theme="bad")
    elif mode == "missing":
        req = replace(req, source_dir=tmp_path / "missing")
    elif mode == "file":
        req = replace(req, source_dir=req.source_dir / "A.md")
    elif mode == "empty":
        empty = tmp_path / "empty"
        empty.mkdir()
        req = replace(req, source_dir=empty)
    elif mode == "collision":
        (req.source_dir / "A.MD").write_text("collision")
        if len(list(req.source_dir.glob("A.*"))) < 2:
            pytest.skip("Case-sensitive filesystem required")
    elif mode == "index":
        (req.source_dir / "index.md").write_text("index")
    elif mode in ("index-exists", "index-alias"):
        req.output_dir.mkdir()
        if mode == "index-exists":
            (req.output_dir / "index.html").write_text("old")
        else:
            os.link(req.source_dir / "A.md", req.output_dir / "index.html")
            req = replace(req, overwrite=True)
    else:
        req.output_dir.write_text("file")

    def forbidden(*args):
        pytest.fail("publication before preflight completed")

    monkeypatch.setattr(HtmlPublicationService, "publish", forbidden)
    with pytest.raises(BatchHtmlPublicationError) as error:
        service().publish(req)
    assert error.value.code == "BATCH_HTML_PREFLIGHT_FAILED"
    assert error.value.__cause__ is not None


def test_output_directory_symlink(tmp_path):
    req = request(tmp_path)
    target = tmp_path / "target"
    target.mkdir()
    try:
        req.output_dir.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("symlink privilege unavailable")
    with pytest.raises(BatchHtmlPublicationError):
        service().publish(req)


@pytest.mark.parametrize("all_fail", [False, True])
def test_partial_and_empty_index(tmp_path, all_fail):
    req = request(tmp_path, index=True)
    (req.source_dir / "A.md").write_bytes(b"\xff")
    if all_fail:
        (req.source_dir / "b.MD").write_bytes(b"\xff")
    result = service().publish(req)
    assert result.items[0].execution.final_job.status is JobStatus.FAILED
    assert result.items[0].execution.pipeline_result.output is None
    html = result.index.output.read_text(encoding="utf-8")
    assert "./A.html" not in html
    assert ("./b.html" in html) is not all_fail


@pytest.mark.parametrize("mode", ["race", "alias", "cleanup"])
def test_independent_index_and_postcommit_failures(tmp_path, monkeypatch, caplog, mode):
    req = request(tmp_path, index=True, overwrite=mode != "race")
    original = WriteStage.execute
    contexts = []

    def execute(self, value, context):
        contexts.append(context)
        if mode == "cleanup":

            def cleanup():
                raise OSError("secret-exception")

            context.register_cleanup(cleanup)
        result = original(self, value, context)
        index = req.output_dir / "index.html"
        if mode == "race":
            index.write_text("competitor")
        elif mode == "alias" and not index.exists():
            os.link(result.output, index)
        return result

    monkeypatch.setattr(WriteStage, "execute", execute)
    caplog.set_level(logging.INFO, logger="test.batch_pipeline")
    result = service().publish(req)
    assert len(contexts) == 2 and contexts[0] is not contexts[1]
    assert all(p.output.exists() for p in result.items)
    if mode == "cleanup":
        assert all(
            p.execution.final_job.status is JobStatus.FAILED for p in result.items
        )
        assert "./A.html" not in result.index.output.read_text(encoding="utf-8")
    else:
        assert result.index is None
        assert result.index_failure.code == "BATCH_INDEX_FAILED"
        with pytest.raises(ValueError):
            replace(result, index=result.items[0].execution.pipeline_result.output)
    assert "secret-exception" not in caplog.text
    assert str(req.source_dir) not in caplog.text


def test_item_race_cleanup_and_single_attempts(tmp_path, monkeypatch):
    req = request(tmp_path)
    original = os.link
    attempts = []

    def race(src, dst):
        attempts.append(Path(dst).name)
        Path(dst).write_text("competitor")
        return original(src, dst)

    monkeypatch.setattr(os, "link", race)
    result = service().publish(req)
    assert attempts == ["A.html", "b.html"]
    assert all(p.execution.final_job.status is JobStatus.FAILED for p in result.items)
    assert not list(req.output_dir.glob(".bgdx-*.tmp"))


def test_runtime_and_unexpected_dependency(tmp_path, monkeypatch):
    req = request(tmp_path)
    app = PublisherApplication()
    app.initialize()
    app.start()
    try:
        assert (
            len(
                app.context.services.resolve(BatchHtmlPublicationService)
                .publish(req)
                .items
            )
            == 2
        )
    finally:
        app.stop()

    def broken(*args):
        raise LookupError("programming error")

    publisher = HtmlPublicationService(logging.getLogger("test"))
    monkeypatch.setattr(publisher, "publish", broken)
    with pytest.raises(LookupError):
        service(publisher).publish(replace(req, overwrite=True))
