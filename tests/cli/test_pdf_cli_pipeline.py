"""CLI routing, compatibility and safe pipeline failure diagnostics."""

import logging
from dataclasses import replace

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.pdf_pipeline import PdfPublicationService
from bgdxpublisher.pdf_pipeline.service import ReadStage, RenderStage, WriteStage
from bgdxpublisher.publishing.pdf import PdfPublishingService, PdfRequest
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
    output = tmp_path / "out.pdf"
    return (
        source,
        output,
        ["publish-pdf", str(source), "--output", str(output), "--config", str(config)],
    )


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
@pytest.mark.parametrize("custom", [False, True])
@pytest.mark.parametrize(
    "text",
    [
        "",
        "# Čć Ћирилица\n\n**bold** *italic* `code`\n\n- First\n  - Nested\n\n"
        "3. Third\n\n> Quote\n\n[link](https://example.com) "
        "![alt](https://example.com/i) <script>x</script>",
        "# Multipage Ћирилица\n\n"
        + "Paragraph Čć.\n\n" * 90
        + "```python\n"
        + "print(1)\n" * 70
        + "```",
    ],
)
def test_pdf_routing_and_equivalence(
    tmp_path, monkeypatch, capsys, encoding, custom, text
):
    from pypdf import PdfReader

    source, output, args = inputs(tmp_path)
    source.write_text(text, encoding=encoding)
    request = PdfRequest(
        source,
        tmp_path / "legacy.pdf",
        title="Čć & <title>" if custom else None,
        language="sr-Latn" if custom else "und",
    )
    PdfPublishingService(logging.getLogger("legacy")).publish(request)
    calls = []
    original = PdfPublicationService.publish

    def publish(self, value):
        calls.append(value)
        return original(self, value)

    def forbidden(*args):
        pytest.fail("legacy publish must not run")

    monkeypatch.setattr(PdfPublicationService, "publish", publish)
    monkeypatch.setattr(PdfPublishingService, "publish", forbidden)
    if custom:
        args += ["--title", request.title, "--lang", request.language]
    before = source.read_bytes()
    assert main(args) == 0
    assert calls == [replace(request, output=output)]
    actual, expected = PdfReader(output), PdfReader(request.output)
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
        f"Publication failed: PDF_PUBLICATION_FAILED stage={stage.name}\n"
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
    expected = (
        "PDF_PUBLICATION_FAILED stage=validate"
        if primary_failure
        else "shutdown failed"
    )
    assert adapter_lines(captured.err) == (
        "Runtime cleanup failed: shutdown failed\n" f"Publication failed: {expected}\n"
    )
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
        "Publication failed: PDF_PUBLICATION_FAILED stage=cleanup\n"
    )
    assert "secret-cleanup" not in captured.err
    assert output.read_bytes().startswith(b"%PDF-")


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


@pytest.mark.parametrize(
    "mode,stage",
    [
        ("missing", "validate"),
        ("extension", "validate"),
        ("encoding", "read"),
        ("glyph", "render"),
        ("control", "render"),
        ("font", "render"),
        ("layout", "render"),
    ],
)
def test_real_operational_diagnostics(tmp_path, monkeypatch, capsys, mode, stage):
    from reportlab.pdfbase.ttfonts import TTFError
    from reportlab.platypus.doctemplate import LayoutError

    from bgdxpublisher.publishing.pdf import PdfRenderer

    source, output, args = inputs(tmp_path)
    if mode == "missing":
        source.unlink()
    elif mode == "extension":
        args[3] = str(tmp_path / "bad.html")
    elif mode in ("encoding", "glyph", "control"):
        source.write_bytes(
            {
                "encoding": b"\xff",
                "glyph": "secret-body 漢".encode(),
                "control": b"secret-body \x01",
            }[mode]
        )
    else:

        def fail(*args):
            raise (TTFError if mode == "font" else LayoutError)("secret-cause")

        monkeypatch.setattr(PdfRenderer, "render", fail)
    assert main(args) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert adapter_lines(captured.err) == (
        f"Publication failed: PDF_PUBLICATION_FAILED stage={stage}\n"
    )
    for secret in (
        str(source),
        str(output),
        "secret-body",
        "secret-cause",
        "U+6F22",
        "Traceback",
    ):
        assert secret not in captured.err
    assert not output.exists()


def adapter_lines(stderr):
    """Safe pipeline logs may accompany the exact primary adapter diagnostics."""
    return "".join(
        line + "\n"
        for line in stderr.splitlines()
        if line.startswith(("Publication failed:", "Runtime cleanup failed:"))
    )
