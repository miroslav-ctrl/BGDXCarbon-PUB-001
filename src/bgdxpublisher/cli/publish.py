"""CLI adapter for document publishing."""

import sys
from pathlib import Path

from bgdxpublisher.html_pipeline import HtmlPublicationError, HtmlPublicationService
from bgdxpublisher.publishing import PublishRequest
from bgdxpublisher.publishing.docx import DocxPublishingService, DocxRequest
from bgdxpublisher.publishing.pdf import PdfPublishingService, PdfRequest
from bgdxpublisher.runtime import (
    PublisherApplication,
    RuntimeFoundationError,
    RuntimeState,
)


def run_publish(
    source: Path,
    output: Path,
    overwrite: bool,
    config_path: Path | None,
    title: str | None = None,
    language: str = "und",
    theme: str = "light",
    toc: bool = False,
    docx: bool = False,
    pdf: bool = False,
) -> int:
    """Delegate to the registered publisher and close runtime on failure too."""
    application = PublisherApplication(config_path=config_path)
    result = None
    failure: str | None = None
    try:
        application.initialize()
        application.start()
        if pdf:
            pdf_service = application.context.services.resolve(PdfPublishingService)
            result = pdf_service.publish(
                PdfRequest(source, output, overwrite, title, language)
            )
        elif docx:
            word_service = application.context.services.resolve(DocxPublishingService)
            result = word_service.publish(
                DocxRequest(source, output, overwrite, title, language)
            )
        else:
            service = application.context.services.resolve(HtmlPublicationService)
            result = service.publish(
                PublishRequest(source, output, overwrite, title, language, theme, toc)
            ).publication
    except HtmlPublicationError as error:
        detail = error.result.pipeline_result.failure
        assert detail is not None
        failure = f"{error.code} stage={detail.stage_name}"
    except RuntimeFoundationError as error:
        failure = str(error)
    finally:
        if application.state in (RuntimeState.CONFIGURED, RuntimeState.RUNNING):
            try:
                application.stop()
            except RuntimeFoundationError as error:
                sys.stderr.write(f"Runtime cleanup failed: {error}\n")
                failure = failure or str(error)
    if failure is not None:
        sys.stderr.write(f"Publication failed: {failure}\n")
        return 1
    assert result is not None
    sys.stdout.write(f"Published: {result.output}\n")
    return 0
