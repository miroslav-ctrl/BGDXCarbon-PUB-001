"""Tests for the executable package entry point."""

import json
import runpy


def test_module_entry_point_runs_and_uses_structured_logging(capsys: object) -> None:
    runpy.run_module("bgdxpublisher.__main__", run_name="__main__")
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert json.loads(captured.err)["message"].endswith("started.")
