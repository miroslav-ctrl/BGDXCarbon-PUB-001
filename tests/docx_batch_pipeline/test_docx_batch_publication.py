"""Batch DOCX selection, fidelity, safety and independent execution contracts."""

import logging
import os
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from unittest.mock import Mock
from zipfile import ZipFile

import pytest

from bgdxpublisher.docx_batch_pipeline import (
    BatchDocxItem,
    BatchDocxPublicationError,
    BatchDocxPublicationResult,
    BatchDocxPublicationService,
    BatchDocxRequest,
)
from bgdxpublisher.docx_pipeline import DocxPublicationService
from bgdxpublisher.docx_pipeline.service import RenderStage, WriteStage
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.publishing.docx import DocxRequest
from bgdxpublisher.runtime import PublisherApplication


def request(tmp_path):
    source = tmp_path / "sources"
    source.mkdir()
    (source / "b.MD").write_text(
        "# Čć Ћирилица\n\n**Bold** *italic*\n\n- One\n- Two\n\n[link](https://example.com)",
        encoding="utf-8-sig",
    )
    (source / "A.md").write_text("", encoding="utf-8")
    (source / "index.md").write_text(
        "# Index allowed\n\n3. Three\n\n> Quote", encoding="utf-8"
    )
    (source / "ignore.txt").write_text("ignore")
    (source / "nested.md").mkdir()
    (source / "nested.md" / "nested.md").write_text("ignore")
    return BatchDocxRequest(source, tmp_path / "out", language="sr-Latn")


def service(publisher=None):
    return BatchDocxPublicationService(logging.getLogger("batch-test"), publisher)


def test_fidelity_snapshot_runtime_and_invariants(tmp_path, monkeypatch):
    req = request(tmp_path)
    app = PublisherApplication()
    app.initialize()
    app.start()
    try:
        batch = app.context.services.resolve(BatchDocxPublicationService)
        single = app.context.services.resolve(DocxPublicationService)
        assert batch._publisher is single
        before = {p: p.read_bytes() for p in req.source_dir.iterdir() if p.is_file()}
        calls = []
        original = single.publish

        def publish(child):
            calls.append(child)
            if len(calls) == 1:
                (req.source_dir / "later.md").write_text("not in snapshot")
            return original(child)

        monkeypatch.setattr(single, "publish", publish)
        result = batch.publish(req)
        assert [p.source.name for p in result.items] == ["A.md", "b.MD", "index.md"]
        assert result.success_count == 3 and result.failure_count == 0
        assert calls == [
            DocxRequest(p.source, p.output, False, None, "sr-Latn")
            for p in result.items
        ]
        other = tmp_path / "individual"
        other.mkdir()
        for item in result.items:
            target = other / item.output.name
            original(DocxRequest(item.source, target, language=req.language))
            with ZipFile(target) as expected, ZipFile(item.output) as actual:
                assert set(actual.namelist()) == set(expected.namelist())
                assert all(
                    actual.read(n) == expected.read(n) for n in actual.namelist()
                )
        assert all(p.read_bytes() == b for p, b in before.items())
        ids = {p.execution.final_job.job_id for p in result.items}
        again = batch.publish(replace(req, overwrite=True))
        assert not ids.intersection(p.execution.final_job.job_id for p in again.items)
        assert len({p.execution.final_job.job_id for p in again.items}) == 4
        with pytest.raises(FrozenInstanceError):
            req.overwrite = True
        with pytest.raises(FrozenInstanceError):
            result.items = ()
        for items in [
            (),
            (result.items[0], result.items[0]),
            (result.items[0], replace(result.items[1], source=result.items[0].source)),
            (
                result.items[0],
                replace(
                    result.items[1],
                    output=result.items[0].output,
                    execution=result.items[0].execution,
                ),
            ),
        ]:
            with pytest.raises(ValueError):
                BatchDocxPublicationResult(items)
        assert isinstance(BatchDocxPublicationResult(list(result.items)).items, tuple)
        with pytest.raises(ValueError):
            replace(result.items[0], output=tmp_path / "wrong")
        # Execution envelope itself rejects nonterminal/mismatched status/history.
        with pytest.raises(ValueError):
            replace(
                result.items[0].execution,
                final_job=replace(
                    result.items[0].execution.final_job, status=JobStatus.RUNNING
                ),
            )
    finally:
        app.stop()


@pytest.mark.parametrize(
    "mode",
    [
        "language",
        "missing",
        "file",
        "empty",
        "collision",
        "output-file",
        "destination-dir",
        "hardlink",
        "mkdir",
    ],
)
def test_preflight_no_children_or_early_mkdir(tmp_path, monkeypatch, caplog, mode):
    req = request(tmp_path)
    if mode == "language":
        req = replace(req, language="en_US")
    elif mode == "missing":
        req = replace(req, source_dir=tmp_path / "SECRET-missing")
    elif mode == "file":
        req = replace(req, source_dir=req.source_dir / "A.md")
    elif mode == "empty":
        req = replace(req, source_dir=req.source_dir / "nested.md")
        (req.source_dir / "nested.md").unlink()
    elif mode == "collision":
        (req.source_dir / "a.MD").write_text("collision")
        if len([p for p in req.source_dir.iterdir() if p.stem.casefold() == "a"]) != 2:
            pytest.skip("case-insensitive filesystem")
    elif mode == "output-file":
        req.output_dir.write_text("keep")
    elif mode in ("destination-dir", "hardlink"):
        req.output_dir.mkdir()
        target = req.output_dir / "A.docx"
        if mode == "hardlink":
            os.link(req.source_dir / "b.MD", target)
        else:
            target.mkdir()
    child = Mock()
    mkdir = Mock(side_effect=PermissionError("SECRET-cause"))
    monkeypatch.setattr(Path, "mkdir", mkdir)
    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(BatchDocxPublicationError) as caught,
    ):
        service(child).publish(req)
    child.publish.assert_not_called()
    assert mkdir.call_count == (1 if mode == "mkdir" else 0)
    assert str(caught.value) == caught.value.code == "BATCH_DOCX_PREFLIGHT_FAILED"
    assert caught.value.__cause__ is not None
    assert "SECRET" not in caplog.text and str(tmp_path) not in caplog.text


@pytest.mark.parametrize("overwrite", [False, True])
@pytest.mark.parametrize(
    "mode",
    [
        "root",
        "candidate",
        "dangling-candidate",
        "outdir",
        "output-input",
        "output-unrelated",
        "output-dangling",
    ],
)
def test_symlink_policy_before_work(tmp_path, monkeypatch, overwrite, mode):
    req = replace(request(tmp_path), overwrite=overwrite)
    link = tmp_path / "link"
    target = req.source_dir
    if mode in ("candidate", "dangling-candidate"):
        link = req.source_dir / "linked.md"
        target = req.source_dir / ("A.md" if mode == "candidate" else "missing")
    elif mode == "outdir":
        target = tmp_path / "elsewhere"
        target.mkdir()
        req = replace(req, output_dir=link)
    elif mode.startswith("output-"):
        req.output_dir.mkdir()
        link = req.output_dir / "A.docx"
        target = req.source_dir / "A.md"
        if mode == "output-unrelated":
            target = tmp_path / "other"
            target.write_text("keep")
        elif mode == "output-dangling":
            target = tmp_path / "missing"
    try:
        link.symlink_to(target, target_is_directory=mode in ("root", "outdir"))
    except OSError:
        pytest.skip("symlink privilege unavailable")
    if mode == "root":
        req = replace(req, source_dir=link)
    child = Mock()
    mkdir = Mock(side_effect=AssertionError("mkdir before checks"))
    monkeypatch.setattr(Path, "mkdir", mkdir)
    with pytest.raises(BatchDocxPublicationError):
        service(child).publish(req)
    mkdir.assert_not_called()
    child.publish.assert_not_called()


def test_refusal_mixed_all_failure_overwrite_same_directory(tmp_path, caplog):
    req = request(tmp_path)
    req = replace(req, output_dir=req.source_dir)
    (req.source_dir / "A.docx").write_bytes(b"preserve")
    (req.source_dir / "b.MD").write_bytes(b"\xff")
    result = service().publish(req)
    assert (result.success_count, result.failure_count) == (1, 2)
    assert [
        p.execution.pipeline_result.failure.stage_name for p in result.items[:2]
    ] == ["validate", "read"]
    assert all(p.execution.pipeline_result.output is None for p in result.items[:2])
    assert (req.source_dir / "A.docx").read_bytes() == b"preserve"
    assert service().publish(req).failure_count == 3
    result = service().publish(replace(req, overwrite=True))
    assert (result.success_count, result.failure_count) == (2, 1)
    assert str(tmp_path) not in caplog.text
    assert "\xff" not in caplog.text
    assert not list(req.output_dir.glob(".bgdx-*.tmp"))


@pytest.mark.parametrize("stage", ["render", "write", "cleanup", "unexpected"])
def test_failure_boundaries_and_cleanup(tmp_path, monkeypatch, stage):
    req = request(tmp_path)
    single = DocxPublicationService(logging.getLogger("single"))
    contexts, cleanups, calls = [], [], []
    original_render = RenderStage.execute
    original_write = WriteStage.execute
    original_publish = single.publish

    def render(self, value, context):
        contexts.append(context)
        name = value.options.source.name

        def cleanup():
            cleanups.append(name)
            if stage == "cleanup" and name == "b.MD":
                raise RuntimeError("SECRET-cleanup")

        context.register_cleanup(cleanup)
        if stage == "render" and name == "b.MD":
            raise RuntimeError("SECRET-render")
        return original_render(self, value, context)

    def write(self, value, context):
        if stage == "write" and value.options.source.name == "b.MD":
            raise PermissionError("SECRET-write")
        return original_write(self, value, context)

    def publish(child):
        calls.append(child.source.name)
        if stage == "unexpected" and child.source.name == "b.MD":
            raise RuntimeError("SECRET-unexpected")
        return original_publish(child)

    monkeypatch.setattr(RenderStage, "execute", render)
    monkeypatch.setattr(WriteStage, "execute", write)
    monkeypatch.setattr(single, "publish", publish)
    if stage == "unexpected":
        with pytest.raises(RuntimeError, match="SECRET-unexpected"):
            service(single).publish(req)
        assert calls == ["A.md", "b.MD"]
        assert (req.output_dir / "A.docx").exists()
        assert not (req.output_dir / "index.docx").exists()
    else:
        result = service(single).publish(req)
        assert (result.success_count, result.failure_count) == (2, 1)
        failure = result.items[1].execution.pipeline_result
        assert failure.failure.stage_name == stage and failure.output is None
        assert (req.output_dir / "b.docx").exists() == (stage == "cleanup")
        assert (req.output_dir / "index.docx").exists()
        assert len(contexts) == len({id(c) for c in contexts}) == 3
    assert len(cleanups) == len(set(cleanups))
    for context in contexts:
        assert context.close() == ()
    assert not list(req.output_dir.glob(".bgdx-*.tmp"))


@pytest.mark.parametrize("mode", ["race", "replace", "flush", "permissions", "unlink"])
def test_atomic_writer_boundaries(tmp_path, monkeypatch, caplog, mode):
    req = replace(request(tmp_path), overwrite=mode != "race")
    req.output_dir.mkdir()
    destination = req.output_dir / "b.docx"
    if mode != "race":
        destination.write_bytes(b"previous")
    originals = {p: p.read_bytes() for p in req.source_dir.iterdir() if p.is_file()}
    original_link, original_replace, original_fsync = os.link, os.replace, os.fsync
    original_unlink = Path.unlink

    def link(source, output):
        if Path(output) == destination:
            destination.write_bytes(b"competitor")
        return original_link(source, output)

    def commit(source, output):
        if Path(output) == destination and mode in ("replace", "permissions"):
            raise PermissionError("SECRET-permission")
        return original_replace(source, output)

    flushes = []

    def fsync(fd):
        flushes.append(fd)
        if mode == "flush" and len(flushes) == 2:
            raise OSError("SECRET-flush")
        return original_fsync(fd)

    unlinks = []

    def unlink(path, *args, **kwargs):
        # Fail temporary cleanup after commit, without leaving a test artifact.
        original_unlink(path, *args, **kwargs)
        if path.name.startswith(".bgdx-"):
            unlinks.append(path)
            if mode == "unlink" and len(unlinks) == 2:
                raise OSError("SECRET-unlink")

    monkeypatch.setattr(os, "link", link)
    monkeypatch.setattr(os, "replace", commit)
    monkeypatch.setattr(os, "fsync", fsync)
    monkeypatch.setattr(Path, "unlink", unlink)
    result = service().publish(req)
    assert (result.success_count, result.failure_count) == (2, 1)
    assert result.items[1].execution.pipeline_result.failure.stage_name == "write"
    assert (
        destination.read_bytes() == (b"competitor" if mode == "race" else b"previous")
        if mode != "unlink"
        else destination.read_bytes().startswith(b"PK")
    )
    assert all(p.read_bytes() == b for p, b in originals.items())
    assert "SECRET" not in caplog.text and str(tmp_path) not in caplog.text
    assert not list(req.output_dir.glob(".bgdx-*.tmp"))


def test_item_rejects_invalid_terminal_envelope(tmp_path):
    from types import SimpleNamespace

    for status, output, failure in [
        (JobStatus.RUNNING, None, None),
        (JobStatus.FAILED, object(), object()),
        (JobStatus.FAILED, None, None),
    ]:
        execution = SimpleNamespace(
            final_job=SimpleNamespace(status=status),
            pipeline_result=SimpleNamespace(output=output, failure=failure),
        )
        with pytest.raises(ValueError):
            BatchDocxItem(tmp_path / "a.md", tmp_path / "a.docx", execution)
