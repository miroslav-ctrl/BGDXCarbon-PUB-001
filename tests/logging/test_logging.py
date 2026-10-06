"""Tests for structured console and file logging."""

import json
import logging
import sys
from pathlib import Path

from bgdxpublisher.config import LoggingSettings
from bgdxpublisher.logging import LoggerFactory, StructuredFormatter


def test_structured_formatter_emits_timestamped_json() -> None:
    record = logging.LogRecord(
        "publisher", logging.INFO, "test.py", 5, "ready %s", ("now",), None
    )
    result = json.loads(StructuredFormatter().format(record))
    assert result["level"] == "INFO"
    assert result["logger"] == "publisher"
    assert result["message"] == "ready now"
    assert result["timestamp"].endswith("+00:00")


def test_structured_formatter_includes_exception_details() -> None:
    try:
        raise ValueError("bad configuration")
    except ValueError:
        record = logging.LogRecord(
            "publisher", logging.ERROR, "test.py", 7, "failed", (), None
        )
        record.exc_info = sys.exc_info()
    result = json.loads(StructuredFormatter().format(record))
    assert "ValueError: bad configuration" in result["exception"]


def test_logger_factory_configures_console_and_file_handlers(
    tmp_path: Path, capsys: object
) -> None:
    log_path = tmp_path / "nested" / "publisher.log"
    service = LoggerFactory.create(
        "test.publisher.output",
        LoggingSettings(level="DEBUG", console=True, file=log_path),
    )
    service.logger.info("runtime ready")
    service.close()
    service.close()
    assert log_path.exists()
    assert (
        json.loads(log_path.read_text(encoding="utf-8"))["message"] == "runtime ready"
    )
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert json.loads(captured.err)["message"] == "runtime ready"


def test_logger_factory_can_disable_all_handlers() -> None:
    service = LoggerFactory.create(
        "test.publisher.disabled", LoggingSettings(console=False)
    )
    assert service.logger.handlers == []
    service.close()
