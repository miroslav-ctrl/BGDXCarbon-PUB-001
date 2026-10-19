"""Compose PDF publishing while preserving the legacy API and CLI."""

from dataclasses import dataclass
from logging import Logger
from pathlib import Path

from bgdxpublisher.domain import Document, DocumentType, PublisherDomainError
from bgdxpublisher.jobs import JobRequest, JobService, JobStatus
from bgdxpublisher.orchestration import (
    JobExecutionError,
    JobExecutionResult,
    JobExecutionService,
)
from bgdxpublisher.pipeline import PipelineContext, PipelineEngine
from bgdxpublisher.publishing import PublishResult
from bgdxpublisher.publishing.metadata import validate_language, validate_title
from bgdxpublisher.publishing.pdf import PdfRenderer, PdfRequest
from bgdxpublisher.publishing.service import PublishingError, PublishingService


@dataclass(frozen=True, slots=True)
class ValidatedPdfRequest:
    """Validated immutable publication options."""

    source: Path
    output: Path
    overwrite: bool
    title: str
    language: str


@dataclass(frozen=True, slots=True)
class PdfSource:
    """Decoded Markdown and validated options."""

    options: ValidatedPdfRequest
    text: str


@dataclass(frozen=True, slots=True)
class RenderedPdf:
    """Serialized PDF bytes awaiting atomic commit."""

    options: ValidatedPdfRequest
    content: bytes


class ValidateStage:
    """Validate metadata and filesystem policy before reading."""

    name: str = "validate"
    input_type: type[object] = PdfRequest
    output_type: type[object] = ValidatedPdfRequest

    def execute(self, value: object, context: PipelineContext) -> object:
        """Return a validated snapshot without writing output."""
        assert isinstance(value, PdfRequest)
        source = value.source.resolve(strict=True)
        output = value.output.absolute()
        if source == output.resolve() or (output.exists() and source.samefile(output)):
            raise PublishingError("Input and output must be different files.")
        if not source.is_file():
            raise PublishingError("Input must be a regular file.")
        if output.suffix.lower() != ".pdf":
            raise PublishingError("PDF output must have a .pdf extension.")
        PublishingService.validate_output(output, value.overwrite)
        if not output.parent.is_dir():
            raise PublishingError("Output parent must be an existing directory.")
        title = source.stem if value.title is None else value.title
        validate_title(title)
        validate_language(value.language)
        return ValidatedPdfRequest(
            source,
            output,
            value.overwrite,
            title,
            value.language,
        )


class ReadStage:
    """Read one UTF-8 source with optional BOM."""

    name: str = "read"
    input_type: type[object] = ValidatedPdfRequest
    output_type: type[object] = PdfSource

    def execute(self, value: object, context: PipelineContext) -> object:
        """Read the source once."""
        assert isinstance(value, ValidatedPdfRequest)
        return PdfSource(value, value.source.read_text(encoding="utf-8-sig"))


class RenderStage:
    """Reuse the existing renderer without legacy publication logging."""

    name: str = "render"
    input_type: type[object] = PdfSource
    output_type: type[object] = RenderedPdf

    def execute(self, value: object, context: PipelineContext) -> object:
        """Render the decoded source once."""
        assert isinstance(value, PdfSource)
        options = value.options
        content = PdfRenderer().render(value.text, options.title, options.language)
        return RenderedPdf(options, content)


class WriteStage:
    """Commit encoded output through the shared atomic writer."""

    name: str = "write"
    input_type: type[object] = RenderedPdf
    output_type: type[object] = PublishResult

    def execute(self, value: object, context: PipelineContext) -> object:
        """Commit once; subsequent cleanup failures do not roll back output."""
        assert isinstance(value, RenderedPdf)
        content = value.content
        PublishingService.write_bytes(
            value.options.output, content, value.options.overwrite
        )
        return PublishResult(value.options.output, len(content))


@dataclass(frozen=True, slots=True)
class PdfPublicationResult:
    """Consistent immutable publication and completed execution envelope."""

    publication: PublishResult
    execution: JobExecutionResult

    def __post_init__(self) -> None:
        """Reject failed execution or mismatched publication data."""
        if (
            self.execution.final_job.status is not JobStatus.COMPLETED
            or self.execution.pipeline_result.output != self.publication
        ):
            raise ValueError("Publication must match a completed execution.")


class PdfPublicationError(PublisherDomainError):
    """Safe failure wrapper retaining the complete execution cause chain."""

    code = "PDF_PUBLICATION_FAILED"

    def __init__(self, result: JobExecutionResult) -> None:
        """Retain a failed execution without exposing partial output."""
        if result.final_job.status is not JobStatus.FAILED:
            raise ValueError("PdfPublicationError requires a failed execution.")
        self.result = result
        super().__init__(self.code)


class PdfPublicationService:
    """Publish one request with fresh jobs and engine-owned contexts."""

    def __init__(self, logger: Logger) -> None:
        """Compose stateless stages and existing orchestration dependencies."""
        self._jobs = JobService(logger=logger)
        self._execution = JobExecutionService(
            self._jobs,
            PipelineEngine(
                (ValidateStage(), ReadStage(), RenderStage(), WriteStage()), logger
            ),
            logger,
        )

    def publish(self, request: PdfRequest) -> PdfPublicationResult:
        """Publish or raise a typed failure; committed files are not rolled back."""
        document = Document(DocumentType.MARKDOWN, "PDF publication", "pdf-pipeline")
        job = self._jobs.create_job(JobRequest(document))
        for status in (JobStatus.VALIDATED, JobStatus.QUEUED):
            job = self._jobs.transition(job, status)
        try:
            execution = self._execution.execute(job, request)
        except JobExecutionError as error:
            raise PdfPublicationError(error.result) from error
        publication = execution.pipeline_result.output
        assert isinstance(publication, PublishResult)
        return PdfPublicationResult(publication, execution)
