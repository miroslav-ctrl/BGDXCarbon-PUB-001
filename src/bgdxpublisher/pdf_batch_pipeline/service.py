"""Preflight a frozen source snapshot and reuse the single PDF pipeline."""

from dataclasses import dataclass
from logging import Logger
from pathlib import Path

from bgdxpublisher.domain import PublisherDomainError
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.orchestration import JobExecutionResult
from bgdxpublisher.pdf_pipeline import PdfPublicationError, PdfPublicationService
from bgdxpublisher.publishing import PublishResult
from bgdxpublisher.publishing.metadata import validate_language
from bgdxpublisher.publishing.pdf import PdfRequest
from bgdxpublisher.publishing.service import PublishingError


@dataclass(frozen=True, slots=True)
class BatchPdfRequest:
    """Options for nonrecursive PDF publication; no index is generated."""

    source_dir: Path
    output_dir: Path
    overwrite: bool = False
    language: str = "und"


@dataclass(frozen=True, slots=True)
class BatchPdfItem:
    """One terminal execution and its explicit caller-visible paths."""

    source: Path
    output: Path
    execution: JobExecutionResult

    def __post_init__(self) -> None:
        """Require a completed matching output or structured failed result."""
        status = self.execution.final_job.status
        pipeline = self.execution.pipeline_result
        if status is JobStatus.COMPLETED:
            if not isinstance(pipeline.output, PublishResult) or (
                pipeline.output.output != self.output
            ):
                raise ValueError("Completed item must match its publication output.")
        elif status is not JobStatus.FAILED or (
            pipeline.output is not None or pipeline.failure is None
        ):
            raise ValueError("Item requires a terminal consistent execution.")


@dataclass(frozen=True, slots=True)
class BatchPdfPublicationResult:
    """Ordered immutable outcomes with derived success and failure counts."""

    items: tuple[BatchPdfItem, ...]

    def __post_init__(self) -> None:
        """Freeze the snapshot and reject empty or duplicate mappings."""
        object.__setattr__(self, "items", tuple(self.items))
        if not self.items or (
            len({p.source for p in self.items}) != len(self.items)
            or len({p.output for p in self.items}) != len(self.items)
        ):
            raise ValueError("Batch requires nonempty unique source/output mappings.")

    @property
    def success_count(self) -> int:
        """Count only completed jobs; failed cleanup is never success."""
        return sum(
            p.execution.final_job.status is JobStatus.COMPLETED for p in self.items
        )

    @property
    def failure_count(self) -> int:
        """Count failed terminal jobs."""
        return len(self.items) - self.success_count


class BatchPdfPublicationError(PublisherDomainError):
    """Expected preflight failure before any child publication was attempted."""

    code = "BATCH_PDF_PREFLIGHT_FAILED"

    def __init__(self) -> None:
        """Expose only a stable code; retain the internal cause chain."""
        super().__init__(self.code)


def _preflight(request: BatchPdfRequest) -> tuple[tuple[Path, ...], Path]:
    """Perform read-only safety checks before directory setup or child calls."""
    validate_language(request.language)
    if request.source_dir.is_symlink():
        raise PublishingError("Source root must not be a symlink.")
    source = request.source_dir.resolve(strict=True)
    if not source.is_dir():
        raise PublishingError("Source must be a directory.")
    candidates = tuple(p for p in source.iterdir() if p.suffix.lower() == ".md")
    if any(p.is_symlink() for p in candidates):
        raise PublishingError("Source candidates must not be symlinks.")
    sources = tuple(
        sorted(
            (p for p in candidates if p.is_file()),
            key=lambda p: (p.name.casefold(), p.name),
        )
    )
    names = [p.stem.casefold() for p in sources]
    if not names or len(names) != len(set(names)):
        raise PublishingError("Empty or ambiguous source selection.")
    output = request.output_dir.absolute()
    if output.is_symlink() or (output.exists() and not output.is_dir()):
        raise PublishingError("Output must be a nonsymlink directory.")
    for item in sources:
        destination = output / (item.stem + ".pdf")
        if destination.is_symlink() or destination.is_dir():
            raise PublishingError("Unsafe output destination.")
        if any(
            destination == p or (destination.exists() and destination.samefile(p))
            for p in sources
        ):
            raise PublishingError("Output aliases a selected input.")
    output.mkdir(parents=True, exist_ok=True)
    return sources, output


class BatchPdfPublicationService:
    """Compose single-document jobs without owning the runtime lifecycle."""

    def __init__(
        self, logger: Logger, publisher: PdfPublicationService | None = None
    ) -> None:
        """Use an injected single publisher, or construct one for direct use."""
        self._logger = logger
        self._publisher = (
            publisher if publisher is not None else PdfPublicationService(logger)
        )

    def publish(self, request: BatchPdfRequest) -> BatchPdfPublicationResult:
        """Continue typed item failures; propagate unexpected child exceptions."""
        try:
            sources, output = _preflight(request)
        except (OSError, ValueError, PublishingError) as error:
            self._logger.error("BATCH_PDF_PREFLIGHT_FAILED")
            raise BatchPdfPublicationError() from error
        items = []
        for source in sources:
            destination = output / (source.stem + ".pdf")
            child = PdfRequest(
                source, destination, request.overwrite, None, request.language
            )
            try:
                execution = self._publisher.publish(child).execution
            except PdfPublicationError as error:
                execution = error.result
            items.append(BatchPdfItem(source, destination, execution))
        return BatchPdfPublicationResult(tuple(items))
