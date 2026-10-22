"""Body/stop stream ordering, primary exception identity and startup state matrix."""

import logging
from types import SimpleNamespace

import pytest

from bgdxpublisher.cli.pdf_batch import run_pdf_batch
from bgdxpublisher.pdf_batch_pipeline import (
    BatchPdfPublicationError,
    BatchPdfPublicationService,
    BatchPdfRequest,
)
from bgdxpublisher.runtime import (
    RuntimeFoundationError,
    RuntimeState,
)


@pytest.mark.parametrize(
    "body", ["success", "mixed", "all", "preflight", "runtime", "unexpected"]
)
@pytest.mark.parametrize("stop", ["success", "runtime", "unexpected"])
def test_body_stop_matrix(tmp_path, monkeypatch, capsys, body, stop):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.md").write_text("# A")
    (source / "b.md").write_bytes(b"\xff" if body in ("mixed", "all") else b"# B")
    if body == "all":
        (source / "a.md").write_bytes(b"\xff")
    result = BatchPdfPublicationService(logging.getLogger("seed")).publish(
        BatchPdfRequest(source, tmp_path / "out")
    )
    capsys.readouterr()
    primary = RuntimeError("SECRET-primary")
    secondary = ValueError("SECRET-stop")
    calls = []
    observed = []

    class App:
        state = RuntimeState.CREATED

        def __init__(self, config_path):
            calls.append(("construct", config_path))
            self.context = SimpleNamespace(
                services=SimpleNamespace(resolve=self.resolve)
            )

        def initialize(self):
            calls.append("initialize")
            self.state = RuntimeState.CONFIGURED

        def start(self):
            calls.append("start")
            self.state = RuntimeState.RUNNING

        def resolve(self, kind):
            calls.append(("resolve", kind))
            assert kind is BatchPdfPublicationService
            return self

        def publish(self, request):
            calls.append(("publish", request))
            assert request == BatchPdfRequest(source, tmp_path / "out", False, "und")
            if body == "unexpected":
                raise primary
            if body == "runtime":
                raise RuntimeFoundationError("runtime-body")
            if body == "preflight":
                raise BatchPdfPublicationError() from ValueError("SECRET-cause")
            return result

        def stop(self):
            calls.append("stop")
            captured = capsys.readouterr()
            assert captured.out == ""
            observed.append(captured.err)
            self.state = RuntimeState.STOPPED
            if stop == "runtime":
                raise RuntimeFoundationError("runtime-stop")
            if stop == "unexpected":
                raise secondary

    monkeypatch.setattr("bgdxpublisher.cli.pdf_batch.PublisherApplication", App)
    if body == "unexpected" or stop == "unexpected":
        with pytest.raises(Exception) as caught:
            run_pdf_batch(source, tmp_path / "out", False, None, "und")
        assert caught.value is (primary if body == "unexpected" else secondary)
        assert getattr(primary, "__notes__", []) == (
            ["An unexpected runtime cleanup failure occurred."]
            if body == "unexpected" and stop == "unexpected"
            else []
        )
    else:
        assert run_pdf_batch(source, tmp_path / "out", False, None, "und") == int(
            body != "success" or stop != "success"
        )
    captured = capsys.readouterr()
    expected = ""
    if body == "preflight":
        expected = "Batch publication failed: BATCH_PDF_PREFLIGHT_FAILED\n"
    elif body == "runtime":
        expected = "Batch publication failed: runtime-body\n"
    elif body in ("mixed", "all"):
        expected = "".join(
            f"Failed: item={i} PDF_PUBLICATION_FAILED stage=read\n"
            for i in ([2] if body == "mixed" else [1, 2])
        )
    assert observed == [expected]
    assert captured.err == (
        "Runtime cleanup failed: runtime-stop\n" if stop == "runtime" else ""
    )
    if stop == "success" and body in ("success", "mixed", "all"):
        assert (
            captured.out
            == "".join(
                f"Published: {p.output}\n"
                for p in result.items
                if p.execution.final_job.status.value == "completed"
            )
            + f"Batch complete: {result.success_count} published, "
            f"{result.failure_count} failed.\n"
        )
    else:
        assert captured.out == ""
    assert calls[:3] == [("construct", None), "initialize", "start"]
    assert calls[3] == ("resolve", BatchPdfPublicationService) and calls[-1] == "stop"
    assert calls.count("stop") == 1 and len(calls) == 6
    assert (tmp_path / "out" / "a.pdf").exists() == (body != "all")


@pytest.mark.parametrize(
    "failure_state",
    [RuntimeState.CREATED, RuntimeState.FAILED, RuntimeState.CONFIGURED],
)
@pytest.mark.parametrize("unexpected", [False, True])
def test_startup_states(tmp_path, monkeypatch, capsys, failure_state, unexpected):
    calls = []
    primary = ValueError("startup") if unexpected else RuntimeFoundationError("startup")

    class App:
        state = RuntimeState.CREATED

        def __init__(self, config_path):
            pass

        def initialize(self):
            self.state = failure_state
            if failure_state is not RuntimeState.CONFIGURED:
                raise primary

        def start(self):
            raise primary

        def stop(self):
            calls.append("stop")

    monkeypatch.setattr("bgdxpublisher.cli.pdf_batch.PublisherApplication", App)
    if unexpected:
        with pytest.raises(ValueError) as caught:
            run_pdf_batch(tmp_path, tmp_path, False, None, "und")
        assert caught.value is primary
    else:
        assert run_pdf_batch(tmp_path, tmp_path, False, None, "und") == 1
    assert calls == (["stop"] if failure_state is RuntimeState.CONFIGURED else [])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ("" if unexpected else "Batch publication failed: startup\n")


def test_constructor_failure_is_unhandled(tmp_path, monkeypatch, capsys):
    def fail(**kwargs):
        raise RuntimeFoundationError("construct")

    monkeypatch.setattr("bgdxpublisher.cli.pdf_batch.PublisherApplication", fail)
    with pytest.raises(RuntimeFoundationError, match="construct"):
        run_pdf_batch(tmp_path, tmp_path, False, None, "und")
    assert capsys.readouterr().out == ""


def test_real_unexpected_child_keeps_earlier_commit(tmp_path, monkeypatch, capsys):
    from bgdxpublisher.pdf_pipeline import PdfPublicationService

    source = tmp_path / "source"
    source.mkdir()
    for name in ("a", "b", "c"):
        (source / f"{name}.md").write_text(name)
    config = tmp_path / "config.yaml"
    config.write_text(
        "app:\n  name: Test\n  version: 1.1.0\n"
        "logging:\n  level: CRITICAL\n  console: false\n"
    )
    original = PdfPublicationService.publish
    calls = []
    primary = ValueError("SECRET-primary")

    def publish(self, request):
        calls.append(request.source.stem)
        if request.source.stem == "b":
            raise primary
        return original(self, request)

    monkeypatch.setattr(PdfPublicationService, "publish", publish)
    with pytest.raises(ValueError) as caught:
        run_pdf_batch(source, tmp_path / "out", False, config, "und")
    assert caught.value is primary and calls == ["a", "b"]
    assert (tmp_path / "out" / "a.pdf").exists()
    assert not (tmp_path / "out" / "c.pdf").exists()
    assert capsys.readouterr().out == ""
