"""CLI routing, compatibility and safe pipeline failure diagnostics."""

import logging
from dataclasses import replace

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.docx_pipeline import DocxPublicationService
from bgdxpublisher.docx_pipeline.service import ReadStage, RenderStage, WriteStage
from bgdxpublisher.publishing.docx import DocxPublishingService, DocxRequest
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


def inputs(tmp_path):
    source = tmp_path / "secret-source.md"
    source.write_text("# Čćžšđ\n\nЋирилица.\n\n## Heading", encoding="utf-8-sig")
    config = tmp_path / "config.yaml"
    config.write_text(
        "app:\n  name: Test\n  version: '1.1'\nlogging:\n  console: false\n",
        encoding="utf-8",
    )
    output = tmp_path / "out.docx"
    return (
        source,
        output,
        ["publish-docx", str(source), "--output", str(output), "--config", str(config)],
    )


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
@pytest.mark.parametrize("custom", [False, True])
@pytest.mark.parametrize(
    "text",
    [
        "",
        "# Čć Ћирилица\n\n**bold** *italic* `code`\n\n- First\n\n[link](https://example.com)",
    ],
)
def test_docx_routing_and_equivalence(
    tmp_path, monkeypatch, capsys, encoding, custom, text
):
    from zipfile import ZipFile

    source, output, args = inputs(tmp_path)
    source.write_text(text, encoding=encoding)
    request = DocxRequest(
        source,
        tmp_path / "legacy.docx",
        title="Čć & <title>" if custom else None,
        language="sr-Latn" if custom else "und",
    )
    DocxPublishingService(logging.getLogger("legacy")).publish(request)
    calls = []
    original = DocxPublicationService.publish

    def publish(self, value):
        calls.append(value)
        return original(self, value)

    def forbidden(*args):
        pytest.fail("legacy publish must not run")

    monkeypatch.setattr(DocxPublicationService, "publish", publish)
    monkeypatch.setattr(DocxPublishingService, "publish", forbidden)
    if custom:
        args += ["--title", request.title, "--lang", request.language]
    before = source.read_bytes()
    assert main(args) == 0
    assert calls == [replace(request, output=output)]
    with ZipFile(output) as actual, ZipFile(request.output) as expected:
        assert set(actual.namelist()) == set(expected.namelist())
        assert all(actual.read(p) == expected.read(p) for p in actual.namelist())
    assert source.read_bytes() == before
    captured = capsys.readouterr()
    assert captured.out == f"Published: {output.absolute()}\n"
    assert captured.err == ""


@pytest.mark.parametrize("stage", [ReadStage, RenderStage, WriteStage])
def test_safe_stage_errors(tmp_path, monkeypatch, capsys, stage):
    source, output, args = inputs(tmp_path)
    app = PublisherApplication(config_path=tmp_path / "config.yaml")
    monkeypatch.setattr(
        "bgdxpublisher.cli.publish.PublisherApplication", lambda **kw: app
    )

    def fail(*args):
        raise OSError("secret-exception " + str(source))

    monkeypatch.setattr(stage, "execute", fail)
    assert main(args) == 1
    assert app.state is RuntimeState.STOPPED
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.endswith(
        f"Publication failed: DOCX_PUBLICATION_FAILED stage={stage.name}\n"
    )
    assert "secret-exception" not in captured.err
    assert str(source) not in captured.err
    assert "Traceback" not in captured.err
    assert not output.exists()


@pytest.mark.parametrize("primary_failure", [False, True])
def test_shutdown_failure_preserves_primary(
    tmp_path, monkeypatch, capsys, primary_failure
):
    source, output, args = inputs(tmp_path)

    class BrokenStop(PublisherApplication):
        def stop(self):
            super().stop()
            raise RuntimeFoundationError("shutdown failed")

    app = BrokenStop(config_path=tmp_path / "config.yaml")
    monkeypatch.setattr(
        "bgdxpublisher.cli.publish.PublisherApplication", lambda **kw: app
    )
    if primary_failure:
        source.unlink()
    assert main(args) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Runtime cleanup failed: shutdown failed\n" in captured.err
    expected = (
        "DOCX_PUBLICATION_FAILED stage=validate"
        if primary_failure
        else "shutdown failed"
    )
    assert captured.err.endswith(f"Publication failed: {expected}\n")
    assert output.exists() is not primary_failure
    assert app.state is RuntimeState.STOPPED


def test_postcommit_cleanup_failure_retains_output(tmp_path, monkeypatch, capsys):
    _, output, args = inputs(tmp_path)
    original = WriteStage.execute

    def execute(self, value, context):
        def cleanup():
            raise OSError("secret-cleanup")

        context.register_cleanup(cleanup)
        return original(self, value, context)

    monkeypatch.setattr(WriteStage, "execute", execute)
    assert main(args) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.endswith(
        "Publication failed: DOCX_PUBLICATION_FAILED stage=cleanup\n"
    )
    assert "secret-cleanup" not in captured.err
    assert output.read_bytes().startswith(b"PK")


def test_parser_failure_never_initializes_runtime(tmp_path, monkeypatch, capsys):
    _, output, args = inputs(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("runtime must not initialize")

    monkeypatch.setattr("bgdxpublisher.cli.publish.PublisherApplication", forbidden)
    with pytest.raises(SystemExit) as error:
        main(args + ["--lang", "en_US"])
    assert error.value.code == 2
    assert "Language must use" in capsys.readouterr().err
    assert not output.exists()
