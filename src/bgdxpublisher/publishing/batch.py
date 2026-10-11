"""Deterministic, non-recursive batch publishing."""

from dataclasses import dataclass
from pathlib import Path

from .metadata import validate_language
from .service import PublishingError, PublishingService, PublishRequest, PublishResult
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
    index: bool = False


@dataclass(frozen=True, slots=True)
class BatchItem:
    """One attempted publication, with a diagnostic on failure."""

    source: Path
    output: Path
    error: str | None = None


@dataclass(frozen=True, slots=True)
class BatchResult:
    """Document outcomes and a separately reported generated index."""

    items: tuple[BatchItem, ...]
    index: PublishResult | None = None
    index_error: str | None = None


def publish_batch(service: PublishingService, request: BatchRequest) -> BatchResult:
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
        if request.index:
            if "index" in names:
                raise PublishingError(
                    "index.md conflicts with the generated index.html."
                )
            index_output = output_dir / "index.html"
            service.validate_output(index_output, request.overwrite)
            protected = sources + [output_dir / (p.stem + ".html") for p in sources]
            if index_output.exists() and any(
                p.exists() and index_output.samefile(p) for p in protected
            ):
                raise PublishingError(
                    "Index must not alias an input or document output."
                )
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
    index_result = None
    index_error = None
    if request.index:
        entries = [(p.source.stem, p.output.name) for p in results if p.error is None]
        try:
            index_result = service.publish_index(
                output_dir / "index.html",
                entries,
                request.language,
                request.theme,
                request.overwrite,
            )
        except PublishingError as error:
            index_error = str(error)
    return BatchResult(tuple(results), index_result, index_error)
