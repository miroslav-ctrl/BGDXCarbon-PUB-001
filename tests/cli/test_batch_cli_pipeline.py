"""Batch CLI service selection, output contracts and shutdown precedence."""

import logging
from dataclasses import replace

import pytest

from bgdxpublisher.batch_pipeline import BatchHtmlPublicationService
from bgdxpublisher.cli.app import main
from bgdxpublisher.html_pipeline.service import WriteStage
from bgdxpublisher.publishing import PublishingService
from bgdxpublisher.publishing.batch import BatchRequest, publish_batch
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


def inputs(tmp_path):
    source = tmp_path / "secret-input"
    source.mkdir()
    (source / "b.MD").write_text("# Čć Ћирилица\n\n## Heading", encoding="utf-8-sig")
    (source / "A.md").write_text("# A", encoding="utf-8")
    config = tmp_path / "config.yaml"
    config.write_text(
        "app:\n  name: Test\n  version: '1.1'\nlogging:\n  console: false\n",
        encoding="utf-8",
    )
    output = tmp_path / "out"
    args = [
        "publish-batch",
        str(source),
        "--output-dir",
        str(output),
        "--config",
        str(config),
    ]
    return source, output, args


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("toc", [False, True])
@pytest.mark.parametrize("index", [False, True])
@pytest.mark.parametrize("language", ["und", "sr-Latn"])
def test_routing_and_equivalence(
    tmp_path, monkeypatch, capsys, theme, toc, index, language
):
    source, output, args = inputs(tmp_path)
    request = BatchRequest(
        source,
        tmp_path / "legacy",
        language=language,
        theme=theme,
        toc=toc,
        index=index,
    )
    publish_batch(PublishingService(logging.getLogger("legacy")), request)
    before = {p: p.read_bytes() for p in source.iterdir()}
    calls = []
    original = BatchHtmlPublicationService.publish

    def publish(self, value):
        calls.append(value)
        return original(self, value)

    def forbidden(*args):
        pytest.fail("legacy batch route invoked")

    monkeypatch.setattr(BatchHtmlPublicationService, "publish", publish)
    monkeypatch.setattr("bgdxpublisher.publishing.batch.publish_batch", forbidden)
    monkeypatch.setattr(PublishingService, "publish", forbidden)
    args += ["--theme", theme, "--lang", language]
    if toc:
        args += ["--toc"]
    if index:
        args += ["--index"]
    assert main(args) == 0
    assert calls == [replace(request, output_dir=output)]
    assert {p.name: p.read_bytes() for p in output.iterdir()} == {
        p.name: p.read_bytes() for p in request.output_dir.iterdir()
    }
    assert all(p.read_bytes() == content for p, content in before.items())
    captured = capsys.readouterr()
    expected = (
        f"Published: {output / 'A.html'}\nPublished: {output / 'b.html'}\n"
        "Batch complete: 2 published, 0 failed.\n"
    )
    if index:
        expected += f"Index published: {output / 'index.html'}\n"
    assert captured.out == expected
    assert captured.err == ""


@pytest.mark.parametrize(
    "mode", ["success", "partial", "preflight", "index", "unexpected"]
)
@pytest.mark.parametrize("stop_failure", [False, True])
def test_shutdown_and_primary(tmp_path, monkeypatch, capsys, mode, stop_failure):
    source, output, args = inputs(tmp_path)
    calls = []
    before_stop = []

    class Application(PublisherApplication):
        def initialize(self):
            calls.append("initialize")
            super().initialize()

        def start(self):
            calls.append("start")
            super().start()

        def stop(self):
            calls.append("stop")
            # CLI output must be delayed until after shutdown.
            captured = capsys.readouterr()
            assert captured.out == ""
            before_stop.append(captured.err)
            super().stop()
            if stop_failure:
                raise RuntimeFoundationError("shutdown failed")

    app = Application(config_path=tmp_path / "config.yaml")
    monkeypatch.setattr(
        "bgdxpublisher.cli.batch.PublisherApplication", lambda **kw: app
    )
    if mode == "partial":
        (source / "A.md").write_bytes(b"\xff")
    elif mode == "preflight":
        args[1] = str(source / "missing")
    elif mode == "index":
        original = WriteStage.execute

        def execute(self, value, context):
            result = original(self, value, context)
            (output / "index.html").write_text("competitor")
            return result

        monkeypatch.setattr(WriteStage, "execute", execute)
        args += ["--index"]
    elif mode == "unexpected":

        def broken(*args):
            raise LookupError("programming failure")

        monkeypatch.setattr(BatchHtmlPublicationService, "publish", broken)
    if mode == "unexpected":
        with pytest.raises(LookupError, match="programming failure"):
            main(args)
    else:
        assert main(args) == int(mode != "success" or stop_failure)
    captured = capsys.readouterr()
    assert calls == ["initialize", "start", "stop"]
    assert app.state is RuntimeState.STOPPED
    if stop_failure or mode in ("preflight", "unexpected"):
        assert captured.out == ""
    else:
        assert "Batch complete:" in captured.out
    assert ("Runtime cleanup failed: shutdown failed" in captured.err) is stop_failure
    diagnostics = "".join(before_stop) + captured.err
    primary_message = {
        "partial": "Failed: item=1 HTML_PUBLICATION_FAILED stage=read\n",
        "preflight": "Batch publication failed: BATCH_HTML_PREFLIGHT_FAILED\n",
        "index": "Index publication failed: BATCH_INDEX_FAILED\n",
    }.get(mode)
    if primary_message:
        assert primary_message in diagnostics
        if stop_failure:
            assert diagnostics.index(primary_message) < diagnostics.index(
                "Runtime cleanup failed:"
            )
    assert str(source) not in diagnostics and "Traceback" not in diagnostics
    if mode in ("success", "partial", "index"):
        assert (output / "b.html").exists()
    if mode == "index":
        assert (output / "index.html").read_text() == "competitor"


@pytest.mark.parametrize("all_fail", [False, True])
def test_partial_and_empty_index_diagnostics(tmp_path, capsys, caplog, all_fail):
    source, output, args = inputs(tmp_path)
    (source / "A.md").write_bytes(b"\xff")
    if all_fail:
        (source / "b.MD").write_bytes(b"\xff")
    caplog.set_level(logging.INFO)
    assert main(args + ["--index"]) == 1
    captured = capsys.readouterr()
    expected = "Failed: item=1 HTML_PUBLICATION_FAILED stage=read\n"
    if all_fail:
        expected += "Failed: item=2 HTML_PUBLICATION_FAILED stage=read\n"
    diagnostics = "".join(
        line + "\n" for line in captured.err.splitlines() if line.startswith("Failed:")
    )
    assert diagnostics == expected
    assert f"{int(not all_fail)} published, {1 + int(all_fail)} failed" in captured.out
    html = (output / "index.html").read_text(encoding="utf-8")
    assert "./A.html" not in html
    assert ("./b.html" in html) is not all_fail
    assert str(source) not in captured.err + caplog.text
    assert "Ћирилица" not in captured.err + caplog.text


def test_postcommit_cleanup_and_primary_diagnostics(tmp_path, monkeypatch, capsys):
    _, output, args = inputs(tmp_path)
    original = WriteStage.execute

    def execute(self, value, context):
        def cleanup():
            raise OSError("secret-cleanup")

        context.register_cleanup(cleanup)
        return original(self, value, context)

    class Application(PublisherApplication):
        def stop(self):
            super().stop()
            raise RuntimeFoundationError("shutdown failed")

    monkeypatch.setattr("bgdxpublisher.cli.batch.PublisherApplication", Application)
    monkeypatch.setattr(WriteStage, "execute", execute)
    assert main(args + ["--index"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    diagnostics = "".join(
        line + "\n"
        for line in captured.err.splitlines()
        if line.startswith(("Failed:", "Runtime cleanup failed:"))
    )
    assert diagnostics == (
        "Failed: item=1 HTML_PUBLICATION_FAILED stage=cleanup\n"
        "Failed: item=2 HTML_PUBLICATION_FAILED stage=cleanup\n"
        "Runtime cleanup failed: shutdown failed\n"
    )
    assert (output / "A.html").exists() and (output / "b.html").exists()
    assert "./A.html" not in (output / "index.html").read_text()


@pytest.mark.parametrize("primary", [False, True])
def test_unexpected_shutdown_exception(tmp_path, monkeypatch, primary):
    _, _, args = inputs(tmp_path)

    class Application(PublisherApplication):
        def stop(self):
            super().stop()
            raise ValueError("broken shutdown")

    monkeypatch.setattr("bgdxpublisher.cli.batch.PublisherApplication", Application)
    if primary:

        def fail(*args):
            raise LookupError("primary")

        monkeypatch.setattr(BatchHtmlPublicationService, "publish", fail)
    with pytest.raises(LookupError if primary else ValueError) as error:
        main(args)
    if primary:
        assert error.value.__notes__ == [
            "An unexpected runtime cleanup failure occurred."
        ]


def test_parser_rejection_before_runtime(tmp_path, monkeypatch):
    _, _, args = inputs(tmp_path)

    def forbidden(**kwargs):
        pytest.fail("runtime constructed after parser rejection")

    monkeypatch.setattr("bgdxpublisher.cli.batch.PublisherApplication", forbidden)
    with pytest.raises(SystemExit) as error:
        main(args + ["--lang", "en_US"])
    assert error.value.code == 2
