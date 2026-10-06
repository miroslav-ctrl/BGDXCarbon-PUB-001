"""Structured standard-library logging services."""

import json
import logging
from datetime import datetime, timezone
from logging import Handler, Logger
from pathlib import Path

from bgdxpublisher.config.models import LoggingSettings


class StructuredFormatter(logging.Formatter):
    """Format standard logging records as timestamped JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize a record with stable structured fields."""
        fields: dict[str, str] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            fields["exception"] = self.formatException(record.exc_info)
        return json.dumps(fields, ensure_ascii=False)


class LoggingService:
    """Own configured handlers and expose the application logger."""

    def __init__(self, logger: Logger, handlers: list[Handler]) -> None:
        """Create a logging service.

        Args:
            logger: Configured standard-library logger.
            handlers: Handlers owned by this service.
        """
        self.logger = logger
        self._handlers = handlers
        self._closed = False

    def close(self) -> None:
        """Flush and close all handlers owned by this service."""
        if self._closed:
            return
        for handler in self._handlers:
            self.logger.removeHandler(handler)
            handler.flush()
            handler.close()
        self._closed = True


class LoggerFactory:
    """Create consistently configured standard-library loggers."""

    @staticmethod
    def create(name: str, settings: LoggingSettings) -> LoggingService:
        """Configure console and optional file handlers.

        Args:
            name: Logger name.
            settings: Validated logging configuration.
        """
        logger = logging.getLogger(name)
        logger.setLevel(settings.level)
        logger.propagate = False
        for old_handler in logger.handlers[:]:
            logger.removeHandler(old_handler)
            old_handler.close()

        formatter = StructuredFormatter()
        handlers: list[Handler] = []
        if settings.console:
            handlers.append(logging.StreamHandler())
        if settings.file is not None:
            log_path: Path = settings.file
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
        for handler in handlers:
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return LoggingService(logger, handlers)
