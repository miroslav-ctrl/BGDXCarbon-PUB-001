"""Batch orchestration; document and index commits are independent."""

from dataclasses import dataclass, field
from logging import Logger
from pathlib import Path

from bgdxpublisher.domain import PublisherDomainError
from bgdxpublisher.html_pipeline import HtmlPublicationError, HtmlPublicationService
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.orchestration import JobExecutionResult
from bgdxpublisher.publishing import PublishRequest, PublishResult
from bgdxpublisher.publishing.batch import BatchRequest
from bgdxpublisher.publishing.metadata import validate_language
from bgdxpublisher.publishing.renderer import HtmlRenderer
from bgdxpublisher.publishing.service import PublishingError, PublishingService
from bgdxpublisher.publishing.themes import THEMES


@dataclass(frozen=True, slots=True)
class BatchHtmlItem:
    """One immutable terminal document execution."""

    source: Path
    output: Path
    execution: JobExecutionResult

    def __post_init__(self) -> None:
        """Require a matching completed publication or a failed execution."""
        if self.execution.final_job.status is JobStatus.COMPLETED:
            result = self.execution.pipeline_result.output
            if not isinstance(result, PublishResult) or result.output != self.output:
                raise ValueError("Completed item must match its publication output.")


@dataclass(frozen=True, slots=True)
class BatchIndexFailure:
    """Safe index diagnostic without exception message or content."""

    exception_type: str
    code: str = field(default="BATCH_INDEX_FAILED", init=False)


@dataclass(frozen=True, slots=True)
class BatchHtmlPublicationResult:
    """Independent item and requested-index outcomes."""

    items: tuple[BatchHtmlItem, ...]
    index_requested: bool = False
    index: PublishResult | None = None
    index_failure: BatchIndexFailure | None = None

    def __post_init__(self) -> None:
        """Freeze the item snapshot and reject ambiguous index outcomes."""
        object.__setattr__(self, "items", tuple(self.items))
        outcomes = int(self.index is not None) + int(self.index_failure is not None)
        if outcomes != int(self.index_requested):
            raise ValueError("Requested index needs exactly one outcome.")


class BatchHtmlPublicationError(PublisherDomainError):
    """Preflight failed before any document publication was attempted."""

    code = "BATCH_HTML_PREFLIGHT_FAILED"

    def __init__(self) -> None:
        """Expose a stable code; the original exception remains the cause."""
        super().__init__(self.code)


def _validate_index(output: Path, sources: tuple[Path, ...], overwrite: bool) -> None:
    """Recheck index policy and aliases before each index commit."""
    destination = output / "index.html"
    PublishingService.validate_output(destination, overwrite)
    protected = (*sources, *(output / (p.stem + ".html") for p in sources))
    if destination.exists() and any(
        p.exists() and destination.samefile(p) for p in protected
    ):
        raise PublishingError("Index aliases a protected file.")


def _preflight(request: BatchRequest) -> tuple[tuple[Path, ...], Path]:
    """Discover deterministic input and reject ambiguous batch destinations."""
    validate_language(request.language)
    if request.theme not in THEMES:
        raise ValueError("Invalid theme.")
    source = request.source_dir.resolve(strict=True)
    if not source.is_dir():
        raise PublishingError("Source must be a directory.")
    sources = tuple(
        sorted(
            (p for p in source.iterdir() if p.suffix.lower() == ".md" and p.is_file()),
            key=lambda p: (p.name.casefold(), p.name),
        )
    )
    if not sources:
        raise PublishingError("No Markdown inputs.")
    names = [p.stem.casefold() for p in sources]
    if len(names) != len(set(names)):
        raise PublishingError("Duplicate destinations.")
    output = request.output_dir.absolute()
    if output.is_symlink():
        raise PublishingError("Output directory must not be a symlink.")
    if request.index:
        if "index" in names:
            raise PublishingError("index.md conflicts with index output.")
        _validate_index(output, sources, request.overwrite)
    output.mkdir(parents=True, exist_ok=True)
    return sources, output


class BatchHtmlPublicationService:
    """Publish sequentially, continuing after expected item failures."""

    def __init__(
        self, logger: Logger, publisher: HtmlPublicationService | None = None
    ) -> None:
        """Compose a publisher without retaining per-batch state."""
        self._logger = logger
        self._publisher = (
            publisher if publisher is not None else HtmlPublicationService(logger)
        )

    def publish(self, request: BatchRequest) -> BatchHtmlPublicationResult:
        """Return item/index outcomes or raise a safe preflight error."""
        try:
            sources, output = _preflight(request)
        except (OSError, ValueError, PublishingError) as error:
            self._logger.error("BATCH_HTML_PREFLIGHT_FAILED")
            raise BatchHtmlPublicationError() from error
        items = []
        for source in sources:
            destination = output / (source.stem + ".html")
            item_request = PublishRequest(
                source,
                destination,
                request.overwrite,
                None,
                request.language,
                request.theme,
                request.toc,
            )
            try:
                execution = self._publisher.publish(item_request).execution
            except HtmlPublicationError as error:
                execution = error.result
            items.append(BatchHtmlItem(source, destination, execution))
        index = None
        failure = None
        if request.index:
            try:
                _validate_index(output, sources, request.overwrite)
                entries = [
                    (p.source.stem, p.output.name)
                    for p in items
                    if p.execution.final_job.status is JobStatus.COMPLETED
                ]
                content = (
                    HtmlRenderer()
                    .render_index(entries, request.language, request.theme)
                    .encode("utf-8")
                )
                PublishingService.write_bytes(
                    output / "index.html", content, request.overwrite
                )
                index = PublishResult(output / "index.html", len(content))
            except (OSError, ValueError, PublishingError) as error:
                failure = BatchIndexFailure(type(error).__name__)
                self._logger.error("BATCH_INDEX_FAILED")
        return BatchHtmlPublicationResult(tuple(items), request.index, index, failure)
