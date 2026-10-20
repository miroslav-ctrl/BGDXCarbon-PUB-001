"""DOCX-specific runtime precedence without altering other dispatch routes."""

from types import SimpleNamespace

import pytest

from bgdxpublisher.cli.publish import run_publish
from bgdxpublisher.docx_pipeline import DocxPublicationService
from bgdxpublisher.html_pipeline import HtmlPublicationService
from bgdxpublisher.pdf_pipeline import PdfPublicationService
from bgdxpublisher.publishing import PublishResult
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


@pytest.mark.parametrize("docx_route", [False, True])
@pytest.mark.parametrize("primary", [False, True])
def test_unexpected_shutdown_precedence(tmp_path, monkeypatch, docx_route, primary):
    source = tmp_path / "source.md"
    source.write_text("# A", encoding="utf-8")

    class Application(PublisherApplication):
        def stop(self):
            super().stop()
            raise ValueError("broken stop")

    monkeypatch.setattr("bgdxpublisher.cli.publish.PublisherApplication", Application)
    if primary:

        def fail(*args):
            raise LookupError("primary")

        monkeypatch.setattr(
            DocxPublicationService if docx_route else HtmlPublicationService,
            "publish",
            fail,
        )
    expected = LookupError if docx_route and primary else ValueError
    with pytest.raises(expected) as error:
        run_publish(
            source,
            tmp_path / ("out.docx" if docx_route else "out.html"),
            False,
            None,
            docx=docx_route,
        )
    if docx_route and primary:
        assert error.value.__notes__ == [
            "An unexpected runtime cleanup failure occurred."
        ]


def test_pdf_first_when_both_flags(tmp_path, monkeypatch, capsys):
    calls = []

    def pdf(self, request):
        calls.append(request)
        return SimpleNamespace(publication=PublishResult(request.output, 0))

    def forbidden(*args):
        pytest.fail("DOCX must not override PDF-first precedence")

    monkeypatch.setattr(PdfPublicationService, "publish", pdf)
    monkeypatch.setattr(DocxPublicationService, "publish", forbidden)
    output = tmp_path / "out.pdf"
    assert (
        run_publish(
            tmp_path / "in.md",
            output,
            True,
            None,
            "Title",
            "sr-Latn",
            docx=True,
            pdf=True,
        )
        == 0
    )
    assert len(calls) == 1 and calls[0].title == "Title"
    assert calls[0].overwrite and calls[0].language == "sr-Latn"
    assert capsys.readouterr().out == f"Published: {output}\n"


@pytest.mark.parametrize("failure", ["initialize", "start"])
def test_docx_runtime_failure_lifecycle(tmp_path, monkeypatch, capsys, failure):
    calls = []

    class Application(PublisherApplication):
        def initialize(self):
            calls.append("initialize")
            if failure == "initialize":
                raise RuntimeFoundationError("init failed")
            super().initialize()

        def start(self):
            calls.append("start")
            raise RuntimeFoundationError("start failed")

        def stop(self):
            calls.append("stop")
            super().stop()

    app = Application()
    monkeypatch.setattr(
        "bgdxpublisher.cli.publish.PublisherApplication", lambda **kw: app
    )
    assert (
        run_publish(tmp_path / "in.md", tmp_path / "out.docx", False, None, docx=True)
        == 1
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.endswith(
        f"Publication failed: {'init' if failure == 'initialize' else 'start'} failed\n"
    )
    assert calls == (
        ["initialize"] if failure == "initialize" else ["initialize", "start", "stop"]
    )
    assert app.state is (
        RuntimeState.CREATED if failure == "initialize" else RuntimeState.STOPPED
    )
