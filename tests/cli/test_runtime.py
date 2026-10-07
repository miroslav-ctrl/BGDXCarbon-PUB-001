"""Tests for runtime status command."""

from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from bgdxpublisher.cli.app import main
from bgdxpublisher.cli.runtime import show_runtime_status
from bgdxpublisher.runtime import (
    ApplicationMetadata,
    ApplicationShutdownError,
    RuntimeState,
)


def test_runtime_status_reports_metadata_and_lifecycle_state(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "app:\n  name: Test Publisher\n  version: 1.2.3\n"
        "runtime:\n  environment: test\nlogging:\n  console: false\n",
        encoding="utf-8",
    )
    output = StringIO()

    exit_code = main(["runtime", "status", "--config", str(config_path)], output)

    assert exit_code == 0
    assert "Application: Test Publisher" in output.getvalue()
    assert "Version: 1.2.3" in output.getvalue()
    assert "Environment: test" in output.getvalue()
    assert "Runtime state: CONFIGURED" in output.getvalue()


def test_runtime_status_reports_initialization_error_without_traceback(
    tmp_path: Path,
) -> None:
    output = StringIO()

    exit_code = main(
        ["runtime", "status", "--config", str(tmp_path / "missing.yaml")], output
    )

    assert exit_code == 1
    assert output.getvalue().startswith("Runtime initialization failed:")
    assert "Traceback" not in output.getvalue()


def test_runtime_status_reports_shutdown_failure() -> None:
    class FailingApplication:
        def __init__(self, config_path: Path) -> None:
            self.context = SimpleNamespace(
                metadata=ApplicationMetadata("Test", "1.0"),
                state=RuntimeState.CONFIGURED,
            )
            self.state = RuntimeState.CONFIGURED

        def initialize(self) -> None:
            return

        def start(self) -> None:
            return

        def stop(self) -> None:
            raise ApplicationShutdownError("shutdown failed")

    output = StringIO()

    exit_code = show_runtime_status(
        output, Path("unused.yaml"), FailingApplication  # type: ignore[arg-type]
    )

    assert exit_code == 1
    assert output.getvalue() == "Runtime shutdown failed: shutdown failed\n"
