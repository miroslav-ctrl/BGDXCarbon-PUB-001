"""Batch behavior and lifecycle verification."""

from pathlib import Path

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.publishing import PublishingService
from bgdxpublisher.publishing.batch import BatchRequest, publish_batch
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


def test_batch_continues_and_preserves_existing_outputs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "a.md").write_bytes(b"\xff")
    (source / "b.MD").write_text("# Ћирилица", encoding="utf-8-sig")
    (source / "c.md").write_text("# Changed", encoding="utf-8")
    (source / "ignore.txt").write_text("ignored")
    (source / "nested").mkdir()
    (source / "nested" / "ignored.md").write_text("ignored")
    output = tmp_path / "output"
    output.mkdir()
    (output / "c.html").write_text("old")
    args = [
        "publish-batch",
        str(source),
        "--output-dir",
        str(output),
        "--theme",
        "dark",
        "--lang",
        "sr-Latn",
        "--toc",
    ]
    assert main(args) == 1
    html = (output / "b.html").read_text(encoding="utf-8")
    assert '<html lang="sr-Latn">' in html
    assert "<title>b</title>" in html
    assert "color-scheme:dark" in html
    assert '<nav class="toc"' in html
    assert (output / "c.html").read_text() == "old"
    assert sorted(p.name for p in output.iterdir()) == ["b.html", "c.html"]
    captured = capsys.readouterr()
    assert "1 published, 2 failed" in captured.out
    assert "a.md" in captured.err and "c.md" in captured.err
    (source / "a.md").write_text("# Fixed")
    assert main([*args, "--overwrite"]) == 0
    assert "3 published, 0 failed" in capsys.readouterr().out
    assert "Changed" in (output / "c.html").read_text()


@pytest.mark.parametrize(
    "kind", ["missing", "file", "empty", "output-file", "collision"]
)
def test_batch_preflight(
    tmp_path: Path,
    kind: str,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "input"
    output = tmp_path / "output"
    if kind == "file":
        source.write_text("x")
    elif kind != "missing":
        source.mkdir()
        if kind != "empty":
            (source / "a.md").write_text("# A")
        if kind == "collision":
            # Windows cannot create case-only siblings; simulate their discovery.
            monkeypatch.setattr(
                Path, "iterdir", lambda self: iter([source / "a.md", source / "a.MD"])
            )
            monkeypatch.setattr(Path, "is_file", lambda self: True)
        if kind == "output-file":
            output.write_text("keep")
    assert main(["publish-batch", str(source), "--output-dir", str(output)]) == 1
    assert "Batch publication failed:" in capsys.readouterr().err
    if kind == "output-file":
        assert output.read_text() == "keep"
    else:
        assert not output.exists()


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["x"],
        ["x", "--output-dir", "y", "--lang", "en_US"],
        ["x", "--output-dir", "y", "--theme", "blue"],
    ],
)
def test_batch_argument_errors(args: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["publish-batch", *args])
    assert error.value.code == 2


@pytest.mark.parametrize("failure", ["none", "start", "stop", "initialize"])
def test_batch_lifecycle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    class Application(PublisherApplication):
        starts = 0

        def start(self) -> None:
            self.starts += 1
            if failure == "start":
                raise RuntimeFoundationError("start error")
            super().start()

        def stop(self) -> None:
            super().stop()
            if failure == "stop":
                raise RuntimeFoundationError("stop error")

    app = Application()
    monkeypatch.setattr(
        "bgdxpublisher.cli.batch.PublisherApplication", lambda **kwargs: app
    )
    source = tmp_path / "input"
    source.mkdir()
    (source / "a.md").write_text("# A")
    if failure == "initialize":
        monkeypatch.setattr(
            app,
            "initialize",
            lambda: (_ for _ in ()).throw(RuntimeFoundationError("init error")),
        )
    assert main(
        [
            "publish-batch",
            str(source),
            "--output-dir",
            str(tmp_path / "nested" / "output"),
        ]
    ) == int(failure != "none")
    assert app.starts == int(failure != "initialize")
    assert app.state is (
        RuntimeState.CREATED if failure == "initialize" else RuntimeState.STOPPED
    )


def test_batch_direct_validation_and_symlink_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import logging

    from bgdxpublisher.publishing import PublishingError

    service = PublishingService(logging.getLogger("batch-test"))
    with pytest.raises(PublishingError, match="Language"):
        publish_batch(
            service, BatchRequest(tmp_path, tmp_path / "out", language="en_US")
        )
    (tmp_path / "a.md").write_text("# A")
    monkeypatch.setattr(Path, "is_symlink", lambda self: True)
    with pytest.raises(PublishingError, match="symbolic link"):
        publish_batch(service, BatchRequest(tmp_path, tmp_path / "out"))
