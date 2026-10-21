"""Batch PDF selection, fidelity, safety and independent execution contracts."""

import logging
import os
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from unittest.mock import Mock

import pytest
from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject, StreamObject

from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.pdf_batch_pipeline import (
    BatchPdfItem,
    BatchPdfPublicationError,
    BatchPdfPublicationResult,
    BatchPdfPublicationService,
    BatchPdfRequest,
)
from bgdxpublisher.pdf_pipeline import PdfPublicationService
from bgdxpublisher.pdf_pipeline.service import RenderStage, WriteStage
from bgdxpublisher.publishing.pdf import PdfRequest
from bgdxpublisher.runtime import PublisherApplication


def pdf_value(value):
    """Compare dereferenced resource meaning, independent of object IDs/encoding."""
    if isinstance(value, IndirectObject):
        return pdf_value(value.get_object())
    if isinstance(value, StreamObject):
        return (
            {
                str(k): pdf_value(v)
                for k, v in value.items()
                if k not in ("/Length", "/Filter", "/DecodeParms")
            },
            value.get_data(),
        )
    if isinstance(value, DictionaryObject):
        return {str(k): pdf_value(v) for k, v in value.items()}
    if isinstance(value, ArrayObject):
        return [pdf_value(v) for v in value]
    return value


def assert_pdf_equivalent(actual_path, expected_path):
    """Match complete decoded content/resources and document/page semantics."""
    actual, expected = PdfReader(actual_path), PdfReader(expected_path)
    assert actual.trailer["/Root"]["/Lang"] == expected.trailer["/Root"]["/Lang"]
    # ReportLab uses wall-clock CreationDate/ModDate and variable trailer IDs.
    # All remaining metadata is compared; decoded page/font resources are exact.
    volatile = {"/CreationDate", "/ModDate"}
    assert {k: v for k, v in actual.metadata.items() if k not in volatile} == {
        k: v for k, v in expected.metadata.items() if k not in volatile
    }
    assert len(actual.pages) == len(expected.pages)
    for page, other in zip(actual.pages, expected.pages):
        assert list(page.mediabox) == list(other.mediabox)
        assert float(page.mediabox.width) == pytest.approx(595.276, abs=0.01)
        assert float(page.mediabox.height) == pytest.approx(841.89, abs=0.01)
        assert page.extract_text() == other.extract_text()
        assert page.get_contents().get_data() == other.get_contents().get_data()
        assert pdf_value(page["/Resources"]) == pdf_value(other["/Resources"])

        def links(p):
            return [
                (
                    list(a.get_object()["/Rect"]),
                    pdf_value(a.get_object().get("/A")),
                    a.get_object().get("/Subtype"),
                )
                for a in p.get("/Annots", [])
            ]

        assert links(page) == links(other)


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
    return BatchPdfRequest(source, tmp_path / "out", language="sr-Latn")


def service(publisher=None):
    return BatchPdfPublicationService(logging.getLogger("batch-test"), publisher)


@pytest.mark.parametrize("multipage", [False, True])
def test_fidelity_snapshot_runtime_and_invariants(tmp_path, monkeypatch, multipage):
    req = request(tmp_path)
    if multipage:
        (req.source_dir / "b.MD").write_text(
            "# Čć Ћирилица\n\n" + "Paragraph Čć text.\n\n" * 75, encoding="utf-8-sig"
        )
    app = PublisherApplication()
    app.initialize()
    app.start()
    try:
        batch = app.context.services.resolve(BatchPdfPublicationService)
        single = app.context.services.resolve(PdfPublicationService)
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
            PdfRequest(p.source, p.output, False, None, "sr-Latn") for p in result.items
        ]
        other = tmp_path / "individual"
        other.mkdir()
        for item in result.items:
            target = other / item.output.name
            original(PdfRequest(item.source, target, language=req.language))
            assert_pdf_equivalent(item.output, target)
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
                BatchPdfPublicationResult(items)
        assert isinstance(BatchPdfPublicationResult(list(result.items)).items, tuple)
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
        target = req.output_dir / "A.pdf"
        if mode == "hardlink":
            os.link(req.source_dir / "b.MD", target)
        else:
            target.mkdir()
    child = Mock()
    mkdir = Mock(side_effect=PermissionError("SECRET-cause"))
    monkeypatch.setattr(Path, "mkdir", mkdir)
    with (
        caplog.at_level(logging.ERROR),
        pytest.raises(BatchPdfPublicationError) as caught,
    ):
        service(child).publish(req)
    child.publish.assert_not_called()
    assert mkdir.call_count == (1 if mode == "mkdir" else 0)
    assert str(caught.value) == caught.value.code == "BATCH_PDF_PREFLIGHT_FAILED"
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
        link = req.output_dir / "A.pdf"
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
    with pytest.raises(BatchPdfPublicationError):
        service(child).publish(req)
    mkdir.assert_not_called()
    child.publish.assert_not_called()


def test_refusal_mixed_all_failure_overwrite_same_directory(tmp_path, caplog):
    req = request(tmp_path)
    req = replace(req, output_dir=req.source_dir)
    (req.source_dir / "A.pdf").write_bytes(b"preserve")
    (req.source_dir / "b.MD").write_bytes(b"\xff")
    result = service().publish(req)
    assert (result.success_count, result.failure_count) == (1, 2)
    assert [
        p.execution.pipeline_result.failure.stage_name for p in result.items[:2]
    ] == ["validate", "read"]
    assert all(p.execution.pipeline_result.output is None for p in result.items[:2])
    assert (req.source_dir / "A.pdf").read_bytes() == b"preserve"
    assert service().publish(req).failure_count == 3
    result = service().publish(replace(req, overwrite=True))
    assert (result.success_count, result.failure_count) == (2, 1)
    assert str(tmp_path) not in caplog.text
    assert "\xff" not in caplog.text
    assert not list(req.output_dir.glob(".bgdx-*.tmp"))


@pytest.mark.parametrize("stage", ["render", "write", "cleanup", "unexpected"])
def test_failure_boundaries_and_cleanup(tmp_path, monkeypatch, stage):
    req = request(tmp_path)
    single = PdfPublicationService(logging.getLogger("single"))
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
        assert (req.output_dir / "A.pdf").exists()
        assert not (req.output_dir / "index.pdf").exists()
    else:
        result = service(single).publish(req)
        assert (result.success_count, result.failure_count) == (2, 1)
        failure = result.items[1].execution.pipeline_result
        assert failure.failure.stage_name == stage and failure.output is None
        assert (req.output_dir / "b.pdf").exists() == (stage == "cleanup")
        assert (req.output_dir / "index.pdf").exists()
        assert len(contexts) == len({id(c) for c in contexts}) == 3
    assert len(cleanups) == len(set(cleanups))
    for context in contexts:
        assert context.close() == ()
    assert not list(req.output_dir.glob(".bgdx-*.tmp"))


@pytest.mark.parametrize("mode", ["race", "replace", "flush", "permissions", "unlink"])
def test_atomic_writer_boundaries(tmp_path, monkeypatch, caplog, mode):
    req = replace(request(tmp_path), overwrite=mode != "race")
    req.output_dir.mkdir()
    destination = req.output_dir / "b.pdf"
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
        else destination.read_bytes().startswith(b"%PDF-")
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
            BatchPdfItem(tmp_path / "a.md", tmp_path / "a.pdf", execution)


@pytest.mark.parametrize("mode", ["glyph", "control", "font", "layout", "title"])
def test_pdf_failure_continues_without_leaks(tmp_path, monkeypatch, caplog, mode):
    from reportlab.pdfbase.ttfonts import TTFError
    from reportlab.platypus import LayoutError

    from bgdxpublisher.publishing import PublishingError
    from bgdxpublisher.publishing.pdf import PdfPublishingService, PdfRenderer

    req = request(tmp_path)
    if mode == "glyph":
        (req.source_dir / "b.MD").write_text("Unsupported 漢 SECRET", encoding="utf-8")
    elif mode == "control":
        (req.source_dir / "b.MD").write_text("Bad \x01 SECRET", encoding="utf-8")
    elif mode == "title":
        # Invalid filename-derived title is an individual validate failure.
        from bgdxpublisher.pdf_pipeline import service as single_module

        original_title = single_module.validate_title

        def title(value):
            if value == "b":
                raise ValueError("SECRET-title")
            return original_title(value)

        monkeypatch.setattr(single_module, "validate_title", title)
    else:
        original = PdfRenderer.render

        def render(self, text, title, language):
            if title == "b":
                raise (
                    TTFError("SECRET-font")
                    if mode == "font"
                    else LayoutError("SECRET-layout")
                )
            return original(self, text, title, language)

        monkeypatch.setattr(PdfRenderer, "render", render)
    with caplog.at_level(logging.INFO):
        result = service().publish(req)
    assert (result.success_count, result.failure_count) == (2, 1)
    item = result.items[1]
    assert item.execution.pipeline_result.output is None
    assert item.execution.pipeline_result.failure.stage_name == (
        "validate" if mode == "title" else "render"
    )
    assert (req.output_dir / "index.pdf").exists()
    for secret in ("SECRET", str(tmp_path), "b.MD", "U+6F22", "漢"):
        assert secret not in caplog.text
    # No legacy fallback is needed; direct legacy API retains its error contract.
    if mode == "glyph":
        with pytest.raises(PublishingError, match=r"U\+6F22"):
            PdfPublishingService(logging.getLogger("legacy")).publish(
                PdfRequest(req.source_dir / "b.MD", tmp_path / "legacy.pdf")
            )


def test_never_calls_legacy_and_preserves_request_defaults(tmp_path, monkeypatch):
    from bgdxpublisher.publishing.pdf import PdfPublishingService

    req = request(tmp_path)
    assert BatchPdfRequest(req.source_dir, req.output_dir).language == "und"
    assert BatchPdfRequest(req.source_dir, req.output_dir).overwrite is False
    monkeypatch.setattr(
        PdfPublishingService, "publish", lambda *a: pytest.fail("legacy fallback")
    )
    assert service().publish(req).success_count == 3


def test_observed_reportlab_volatility(tmp_path, monkeypatch):
    from reportlab.lib import utils

    req = request(tmp_path)
    original = utils.time.time
    batch = service().publish(req)
    monkeypatch.setattr(utils.time, "time", lambda: original() + 120)
    later = service().publish(replace(req, output_dir=tmp_path / "later"))
    first, second = PdfReader(batch.items[0].output), PdfReader(later.items[0].output)
    assert first.metadata.creation_date != second.metadata.creation_date
    assert first.metadata.modification_date != second.metadata.modification_date
    assert first.trailer["/ID"] != second.trailer["/ID"]
    for a, b in zip(batch.items, later.items):
        assert_pdf_equivalent(a.output, b.output)
