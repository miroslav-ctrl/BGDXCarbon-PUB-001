"""Publish documents with an atomic, explicit-overwrite filesystem contract."""

import logging
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from bgdxpublisher.exceptions import RuntimeFoundationError

from .renderer import HtmlRenderer


class PublishingError(RuntimeFoundationError):
    """An expected document input, rendering or output error."""


@dataclass(frozen=True, slots=True)
class PublishRequest:
    """Paths and overwrite policy for one publication."""

    source: Path
    output: Path
    overwrite: bool = False
    title: str | None = None
    language: str = "und"
    theme: str = "light"


@dataclass(frozen=True, slots=True)
class PublishResult:
    """Location and UTF-8 byte count of a completed publication."""

    output: Path
    bytes_written: int


class PublishingService:
    """Read, render and commit a single HTML output without modifying input."""

    def __init__(self, logger: logging.Logger) -> None:
        """Use the initialized application's logger."""
        self._logger = logger
        self._renderer = HtmlRenderer()

    def publish(self, request: PublishRequest) -> PublishResult:
        """Publish or raise PublishingError; previous output survives failure."""
        self._logger.info("Publishing document: %s", request.source)
        try:
            result = self._publish(request)
        except (OSError, UnicodeError, ValueError) as error:
            self._logger.error("Publishing failed: %s", error)
            raise PublishingError(f"Unable to publish document: {error}") from error
        except PublishingError as error:
            self._logger.error("Publishing failed: %s", error)
            raise
        self._logger.info("Published document: %s", result.output)
        return result

    def _publish(self, request: PublishRequest) -> PublishResult:
        """Validate paths before reading and commit a fully rendered output."""
        source = request.source.resolve(strict=True)
        output = request.output.absolute()
        if output.is_symlink():
            raise PublishingError("Output must not be a symbolic link.")
        if source == output.resolve() or (output.exists() and source.samefile(output)):
            raise PublishingError("Input and output must be different files.")
        if not source.is_file():
            raise PublishingError("Input must be a regular file.")
        if output.exists():
            if not output.is_file():
                raise PublishingError("Output must be a regular file.")
            if not request.overwrite:
                raise PublishingError("Output exists; use --overwrite to replace it.")
        text = source.read_text(encoding="utf-8-sig")
        title = source.stem if request.title is None else request.title
        html = self._renderer.render(text, title, request.language, request.theme)
        self._write(output, html, request.overwrite)
        return PublishResult(output, len(html.encode("utf-8")))

    @staticmethod
    def _write(output: Path, html: str, overwrite: bool) -> None:
        """Commit in the output directory; hard-link creation refuses races."""
        temporary: Path | None = None
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=output.parent,
                prefix=".bgdx-",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary = Path(stream.name)
                stream.write(html)
                stream.flush()
                os.fsync(stream.fileno())
            if overwrite:
                if os.name == "posix":
                    mode = (
                        stat.S_IMODE(output.stat().st_mode)
                        if output.exists()
                        else 0o644
                    )
                    temporary.chmod(mode)
                os.replace(temporary, output)
            else:
                if os.name == "posix":
                    temporary.chmod(0o644)
                os.link(temporary, output)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
