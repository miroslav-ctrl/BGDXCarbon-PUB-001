"""Compose HTML publishing without changing legacy command routing."""

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
from bgdxpublisher.publishing import PublishRequest, PublishResult
from bgdxpublisher.publishing.metadata import validate_language, validate_title
from bgdxpublisher.publishing.renderer import HtmlRenderer
from bgdxpublisher.publishing.service import PublishingError, PublishingService
from bgdxpublisher.publishing.themes import THEMES


@dataclass(frozen=True, slots=True)
class ValidatedHtmlRequest:
    """Validated immutable publication options."""

    source: Path
    output: Path
    overwrite: bool
    title: str
    language: str
    theme: str
    toc: bool


@dataclass(frozen=True, slots=True)
class HtmlSource:
    """Decoded Markdown and validated options."""

    options: ValidatedHtmlRequest
    text: str


@dataclass(frozen=True, slots=True)
class RenderedHtml:
    """Rendered HTML awaiting atomic commit."""

    options: ValidatedHtmlRequest
    html: str


class ValidateStage:
    """Validate metadata and filesystem policy before reading."""

    name: str = "validate"
    input_type: type[object] = PublishRequest
    output_type: type[object] = ValidatedHtmlRequest

    def execute(self, value: object, context: PipelineContext) -> object:
        """Return a validated snapshot without writing output."""
        assert isinstance(value, PublishRequest)
        source = value.source.resolve(strict=True)
        output = value.output.absolute()
        if source == output.resolve() or (output.exists() and source.samefile(output)):
            raise PublishingError("Input and output must be different files.")
        if not source.is_file():
            raise PublishingError("Input must be a regular file.")
        PublishingService.validate_output(output, value.overwrite)
        if not output.parent.is_dir():
            raise PublishingError("Output parent must be an existing directory.")
        title = source.stem if value.title is None else value.title
        validate_title(title)
        validate_language(value.language)
        if value.theme not in THEMES:
            raise ValueError("Theme must be light or dark.")
        return ValidatedHtmlRequest(
            source,
            output,
            value.overwrite,
            title,
            value.language,
            value.theme,
            value.toc,
        )


class ReadStage:
    """Read one UTF-8 source with optional BOM."""

    name: str = "read"
    input_type: type[object] = ValidatedHtmlRequest
    output_type: type[object] = HtmlSource

    def execute(self, value: object, context: PipelineContext) -> object:
        """Read the source once."""
        assert isinstance(value, ValidatedHtmlRequest)
        return HtmlSource(value, value.source.read_text(encoding="utf-8-sig"))


class RenderStage:
    """Reuse the existing renderer without legacy publication logging."""

    name: str = "render"
    input_type: type[object] = HtmlSource
    output_type: type[object] = RenderedHtml

    def execute(self, value: object, context: PipelineContext) -> object:
        """Render the decoded source once."""
        assert isinstance(value, HtmlSource)
        options = value.options
        html = HtmlRenderer().render(
            value.text, options.title, options.language, options.theme, options.toc
        )
        return RenderedHtml(options, html)


class WriteStage:
    """Commit encoded output through the shared atomic writer."""

    name: str = "write"
    input_type: type[object] = RenderedHtml
    output_type: type[object] = PublishResult

    def execute(self, value: object, context: PipelineContext) -> object:
        """Commit once; subsequent cleanup failures do not roll back output."""
        assert isinstance(value, RenderedHtml)
        content = value.html.encode("utf-8")
        PublishingService.write_bytes(
            value.options.output, content, value.options.overwrite
        )
        return PublishResult(value.options.output, len(content))


@dataclass(frozen=True, slots=True)
class HtmlPublicationResult:
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


class HtmlPublicationError(PublisherDomainError):
    """Safe failure wrapper retaining the complete execution cause chain."""

    code = "HTML_PUBLICATION_FAILED"

    def __init__(self, result: JobExecutionResult) -> None:
        """Retain a failed execution without exposing partial output."""
        if result.final_job.status is not JobStatus.FAILED:
            raise ValueError("HtmlPublicationError requires a failed execution.")
        self.result = result
        super().__init__(self.code)


class HtmlPublicationService:
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

    def publish(self, request: PublishRequest) -> HtmlPublicationResult:
        """Publish or raise a typed failure; committed files are not rolled back."""
        document = Document(DocumentType.MARKDOWN, "HTML publication", "html-pipeline")
        job = self._jobs.create_job(JobRequest(document))
        for status in (JobStatus.VALIDATED, JobStatus.QUEUED):
            job = self._jobs.transition(job, status)
        try:
            execution = self._execution.execute(job, request)
        except JobExecutionError as error:
            raise HtmlPublicationError(error.result) from error
        publication = execution.pipeline_result.output
        assert isinstance(publication, PublishResult)
        return HtmlPublicationResult(publication, execution)
