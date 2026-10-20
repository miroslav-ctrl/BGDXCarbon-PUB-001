"""Explicit PDF shutdown matrix while retaining DOCX and HTML contracts."""

import pytest

from bgdxpublisher.cli.publish import run_publish
from bgdxpublisher.pdf_pipeline import PdfPublicationService
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


@pytest.mark.parametrize("both", [False, True])
@pytest.mark.parametrize("primary", ["success", "typed", "unexpected"])
@pytest.mark.parametrize("stop_error", ["expected", "unexpected"])
def test_pdf_shutdown_matrix(tmp_path, monkeypatch, capsys, both, primary, stop_error):
    config = tmp_path / "config.yaml"
    config.write_text(
        "app:\n  name: Test\n  version: '1.1'\nlogging:\n  console: false\n",
        encoding="utf-8",
    )
    source, output = tmp_path / "source.md", tmp_path / "out.pdf"
    source.write_text("# Source", encoding="utf-8")
    calls = []

    class Application(PublisherApplication):
        def initialize(self):
            calls.append("initialize")
            super().initialize()

        def start(self):
            calls.append("start")
            super().start()

        def stop(self):
            calls.append("stop")
            super().stop()
            raise (RuntimeFoundationError if stop_error == "expected" else ValueError)(
                "broken stop"
            )

    app = Application(config_path=config)
    monkeypatch.setattr(
        "bgdxpublisher.cli.publish.PublisherApplication", lambda **kw: app
    )
    if primary == "typed":
        source.unlink()
    elif primary == "unexpected":

        def fail(*args):
            raise LookupError("primary")

        monkeypatch.setattr(PdfPublicationService, "publish", fail)

    def run():
        return run_publish(source, output, False, config, pdf=True, docx=both)

    if primary == "unexpected":
        with pytest.raises(LookupError, match="primary") as error:
            run()
        if stop_error == "unexpected":
            assert error.value.__notes__ == [
                "An unexpected runtime cleanup failure occurred."
            ]
    elif stop_error == "unexpected":
        with pytest.raises(ValueError, match="broken stop"):
            run()
    else:
        assert run() == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    if stop_error == "expected":
        expected = "Runtime cleanup failed: broken stop\n"
        if primary != "unexpected":
            expected += (
                "Publication failed: "
                + (
                    "PDF_PUBLICATION_FAILED stage=validate"
                    if primary == "typed"
                    else "broken stop"
                )
                + "\n"
            )
        assert adapter_lines(captured.err) == expected
    else:
        assert adapter_lines(captured.err) == ""
    assert output.exists() is (primary == "success")
    assert app.state is RuntimeState.STOPPED
    assert calls == ["initialize", "start", "stop"]


@pytest.mark.parametrize("failure", ["initialize", "start"])
def test_pdf_startup_failure(tmp_path, monkeypatch, capsys, failure):
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
        run_publish(tmp_path / "in.md", tmp_path / "out.pdf", False, None, pdf=True)
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


def adapter_lines(stderr):
    """Exclude allowed safe pipeline logs from primary diagnostic count/order."""
    return "".join(
        line + "\n"
        for line in stderr.splitlines()
        if line.startswith(("Publication failed:", "Runtime cleanup failed:"))
    )
