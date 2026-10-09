"""Deterministic, non-recursive batch publishing."""

from dataclasses import dataclass
from pathlib import Path

from .metadata import validate_language
from .service import PublishingError, PublishingService, PublishRequest
from .themes import theme_css


@dataclass(frozen=True, slots=True)
class BatchRequest:
    """Shared options for immediate Markdown children of a directory."""

    source_dir: Path
    output_dir: Path
    overwrite: bool = False
    language: str = "und"
    theme: str = "light"
    toc: bool = False


@dataclass(frozen=True, slots=True)
class BatchItem:
    """One attempted publication, with a diagnostic on failure."""

    source: Path
    output: Path
    error: str | None = None


def publish_batch(
    service: PublishingService, request: BatchRequest
) -> tuple[BatchItem, ...]:
    """Publish independently; reject ambiguous destinations before writing."""
    try:
        validate_language(request.language)
        theme_css(request.theme)
        source_dir = request.source_dir.resolve(strict=True)
        if not source_dir.is_dir():
            raise PublishingError("Source must be a directory.")
        sources = sorted(
            (
                p
                for p in source_dir.iterdir()
                if p.suffix.lower() == ".md" and p.is_file()
            ),
            key=lambda p: (p.name.casefold(), p.name),
        )
        if not sources:
            raise PublishingError("Source directory contains no Markdown files.")
        names = [p.stem.casefold() for p in sources]
        if len(names) != len(set(names)):
            raise PublishingError(
                "Markdown filenames map to duplicate HTML destinations."
            )
        output_dir = request.output_dir.absolute()
        if output_dir.is_symlink():
            raise PublishingError("Output directory must not be a symbolic link.")
        output_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as error:
        raise PublishingError(str(error)) from error
    results = []
    for source in sources:
        output = output_dir / (source.stem + ".html")
        try:
            service.publish(
                PublishRequest(
                    source,
                    output,
                    request.overwrite,
                    None,
                    request.language,
                    request.theme,
                    request.toc,
                )
            )
        except PublishingError as error:
            results.append(BatchItem(source, output, str(error)))
        else:
            results.append(BatchItem(source, output))
    return tuple(results)
