"""Publishing CLI and lifecycle regression tests."""

from pathlib import Path

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.logging import LoggingService
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


@pytest.mark.parametrize(
    "args", [["publish"], ["publish", "input.md"], ["publish", "input.md", "--unknown"]]
)
def test_publish_requires_valid_arguments(args: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2


@pytest.mark.parametrize("fail", [False, True])
def test_publish_closes_runtime(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fail: bool,
) -> None:
    application = PublisherApplication()
    monkeypatch.setattr(
        "bgdxpublisher.cli.publish.PublisherApplication", lambda **kwargs: application
    )
    source = tmp_path / "source.md"
    if not fail:
        source.write_text("# Test", encoding="utf-8")
    output = tmp_path / "out.html"
    assert main(["publish", str(source), "--output", str(output)]) == int(fail)
    assert application.state is RuntimeState.STOPPED
    captured = capsys.readouterr()
    assert (
        ("Publication failed:" in captured.err)
        if fail
        else ("Published:" in captured.out)
    )


def test_publish_config_and_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("# Custom", encoding="utf-8")
    output = tmp_path / "out.html"
    output.write_text("old", encoding="utf-8")
    config = tmp_path / "config.yaml"
    config.write_text(
        "app:\n  name: Custom\n  version: '1.0'\nlogging:\n  console: false\n",
        encoding="utf-8",
    )
    assert (
        main(
            [
                "publish",
                str(source),
                "--output",
                str(output),
                "--overwrite",
                "--config",
                str(config),
            ]
        )
        == 0
    )
    assert "<h1>Custom</h1>" in output.read_text(encoding="utf-8")


def test_publish_initialization_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert (
        main(
            [
                "publish",
                "input.md",
                "--output",
                "out.html",
                "--config",
                str(tmp_path / "missing.yaml"),
            ]
        )
        == 1
    )
    assert "Publication failed:" in capsys.readouterr().err


def test_cleanup_failure_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class BrokenCleanup(PublisherApplication):
        def stop(self) -> None:
            raise RuntimeFoundationError("cleanup error")

    monkeypatch.setattr("bgdxpublisher.cli.publish.PublisherApplication", BrokenCleanup)
    source = tmp_path / "source.md"
    source.write_text("hello", encoding="utf-8")
    assert main(["publish", str(source), "--output", str(tmp_path / "out.html")]) == 1
    assert "Runtime cleanup failed:" in capsys.readouterr().err


def test_start_failure_still_closes_configured_runtime(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    class FailingFirstStart(PublisherApplication):
        attempts = 0

        def start(self) -> None:
            self.attempts += 1
            raise RuntimeFoundationError("start failed")

    application = FailingFirstStart()
    monkeypatch.setattr(
        "bgdxpublisher.cli.publish.PublisherApplication", lambda **kwargs: application
    )
    output = tmp_path / "out.html"
    assert main(["publish", "missing.md", "--output", str(output)]) == 1
    assert application.state is RuntimeState.STOPPED
    assert application.attempts == 1
    assert not application.context.services.resolve(LoggingService).logger.handlers
    assert "start failed" in capsys.readouterr().err
    assert not output.exists()
