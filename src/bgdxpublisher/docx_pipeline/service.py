"""Compose DOCX publishing while preserving the legacy API and CLI."""

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
from bgdxpublisher.publishing.docx import DocxRenderer, DocxRequest
from bgdxpublisher.publishing.metadata import validate_language, validate_title
from bgdxpublisher.publishing.service import PublishingError, PublishingService


@dataclass(frozen=True, slots=True)
class ValidatedDocxRequest:
    """Validated immutable publication options."""

    source: Path
    output: Path
    overwrite: bool
    title: str
    language: str


@dataclass(frozen=True, slots=True)
class DocxSource:
    """Decoded Markdown and validated options."""

    options: ValidatedDocxRequest
    text: str


@dataclass(frozen=True, slots=True)
class RenderedDocx:
    """Serialized DOCX bytes awaiting atomic commit."""

    options: ValidatedDocxRequest
    content: bytes


class ValidateStage:
    """Validate metadata and filesystem policy before reading."""

    name: str = "validate"
    input_type: type[object] = DocxRequest
    output_type: type[object] = ValidatedDocxRequest

    def execute(self, value: object, context: PipelineContext) -> object:
        """Return a validated snapshot without writing output."""
        assert isinstance(value, DocxRequest)
        source = value.source.resolve(strict=True)
        output = value.output.absolute()
        if source == output.resolve() or (output.exists() and source.samefile(output)):
            raise PublishingError("Input and output must be different files.")
        if not source.is_file():
            raise PublishingError("Input must be a regular file.")
        if output.suffix.lower() != ".docx":
            raise PublishingError("DOCX output must have a .docx extension.")
        PublishingService.validate_output(output, value.overwrite)
        if not output.parent.is_dir():
            raise PublishingError("Output parent must be an existing directory.")
        title = source.stem if value.title is None else value.title
        validate_title(title)
        validate_language(value.language)
        return ValidatedDocxRequest(
            source,
            output,
            value.overwrite,
            title,
            value.language,
        )


class ReadStage:
    """Read one UTF-8 source with optional BOM."""

    name: str = "read"
    input_type: type[object] = ValidatedDocxRequest
    output_type: type[object] = DocxSource

    def execute(self, value: object, context: PipelineContext) -> object:
        """Read the source once."""
        assert isinstance(value, ValidatedDocxRequest)
        return DocxSource(value, value.source.read_text(encoding="utf-8-sig"))


class RenderStage:
    """Reuse the existing renderer without legacy publication logging."""

    name: str = "render"
    input_type: type[object] = DocxSource
    output_type: type[object] = RenderedDocx

    def execute(self, value: object, context: PipelineContext) -> object:
        """Render the decoded source once."""
        assert isinstance(value, DocxSource)
        options = value.options
        content = DocxRenderer().render(value.text, options.title, options.language)
        return RenderedDocx(options, content)


class WriteStage:
    """Commit encoded output through the shared atomic writer."""

    name: str = "write"
    input_type: type[object] = RenderedDocx
    output_type: type[object] = PublishResult

    def execute(self, value: object, context: PipelineContext) -> object:
        """Commit once; subsequent cleanup failures do not roll back output."""
        assert isinstance(value, RenderedDocx)
        content = value.content
        PublishingService.write_bytes(
            value.options.output, content, value.options.overwrite
        )
        return PublishResult(value.options.output, len(content))


@dataclass(frozen=True, slots=True)
class DocxPublicationResult:
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


class DocxPublicationError(PublisherDomainError):
    """Safe failure wrapper retaining the complete execution cause chain."""

    code = "DOCX_PUBLICATION_FAILED"

    def __init__(self, result: JobExecutionResult) -> None:
        """Retain a failed execution without exposing partial output."""
        if result.final_job.status is not JobStatus.FAILED:
            raise ValueError("DocxPublicationError requires a failed execution.")
        self.result = result
        super().__init__(self.code)


class DocxPublicationService:
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

    def publish(self, request: DocxRequest) -> DocxPublicationResult:
        """Publish or raise a typed failure; committed files are not rolled back."""
        document = Document(DocumentType.MARKDOWN, "DOCX publication", "docx-pipeline")
        job = self._jobs.create_job(JobRequest(document))
        for status in (JobStatus.VALIDATED, JobStatus.QUEUED):
            job = self._jobs.transition(job, status)
        try:
            execution = self._execution.execute(job, request)
        except JobExecutionError as error:
            raise DocxPublicationError(error.result) from error
        publication = execution.pipeline_result.output
        assert isinstance(publication, PublishResult)
        return DocxPublicationResult(publication, execution)
