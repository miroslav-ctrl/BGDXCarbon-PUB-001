"""Tests for the executable package entry point."""

import runpy
import sys

import pytest


def test_module_entry_point_displays_cli_help(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["bgdxpublisher", "--help"])

    with pytest.raises(SystemExit) as error:
        runpy.run_module("bgdxpublisher.__main__", run_name="__main__")

    assert error.value.code == 0
    assert "usage: bgdxpublisher" in capsys.readouterr().out
