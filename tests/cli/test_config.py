"""Tests for the configuration validation command."""

from io import StringIO
from pathlib import Path

from bgdxpublisher.cli.app import main

_VALID_CONFIG = """\
app:
  name: Test Publisher
  version: 1.2.3
runtime:
  environment: test
"""


def test_configuration_validation_succeeds(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(_VALID_CONFIG, encoding="utf-8")
    output = StringIO()

    exit_code = main(["config", "validate", "--config", str(config_path)], output)

    assert exit_code == 0
    assert output.getvalue() == "Configuration is valid.\n"


def test_configuration_validation_reports_domain_error_without_traceback(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text("invalid: true\n", encoding="utf-8")
    output = StringIO()

    exit_code = main(["config", "validate", "--config", str(config_path)], output)

    assert exit_code == 1
    assert output.getvalue().startswith("Configuration validation failed:")
    assert "Traceback" not in output.getvalue()


def test_configuration_validation_returns_nonzero_for_missing_file(
    tmp_path: Path,
) -> None:
    output = StringIO()

    exit_code = main(
        ["config", "validate", "--config", str(tmp_path / "missing.yaml")], output
    )

    assert exit_code == 1
    assert "Unable to read configuration file" in output.getvalue()
