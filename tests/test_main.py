"""Tests for the executable package entry point."""

import json
import runpy
import sys

import pytest


def test_module_entry_point_runs_and_uses_structured_logging(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["bgdxpublisher"])
    with pytest.raises(SystemExit) as error:
        runpy.run_module("bgdxpublisher.__main__", run_name="__main__")
    assert error.value.code == 0
    captured = capsys.readouterr()
    assert json.loads(captured.err)["message"] == (
        "BGDXCarbon Publisher Suite 0.1.0 started."
    )
