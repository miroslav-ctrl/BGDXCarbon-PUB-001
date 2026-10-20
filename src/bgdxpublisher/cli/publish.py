"""CLI adapter for document publishing."""

import sys
from pathlib import Path

from bgdxpublisher.docx_pipeline import DocxPublicationError, DocxPublicationService
from bgdxpublisher.html_pipeline import HtmlPublicationError, HtmlPublicationService
from bgdxpublisher.pdf_pipeline import PdfPublicationError, PdfPublicationService
from bgdxpublisher.publishing import PublishRequest
from bgdxpublisher.publishing.docx import DocxRequest
from bgdxpublisher.publishing.pdf import PdfRequest
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
    protected_route = pdf or docx
    try:
        application.initialize()
        application.start()
        if pdf:
            pdf_service = application.context.services.resolve(PdfPublicationService)
            result = pdf_service.publish(
                PdfRequest(source, output, overwrite, title, language)
            ).publication
        elif docx:
            word_service = application.context.services.resolve(DocxPublicationService)
            result = word_service.publish(
                DocxRequest(source, output, overwrite, title, language)
            ).publication
        else:
            service = application.context.services.resolve(HtmlPublicationService)
            result = service.publish(
                PublishRequest(source, output, overwrite, title, language, theme, toc)
            ).publication
    except (HtmlPublicationError, DocxPublicationError, PdfPublicationError) as error:
        detail = error.result.pipeline_result.failure
        assert detail is not None
        failure = f"{error.code} stage={detail.stage_name}"
    except RuntimeFoundationError as error:
        failure = str(error)
    finally:
        if application.state in (RuntimeState.CONFIGURED, RuntimeState.RUNNING):
            primary = sys.exception()
            try:
                application.stop()
            except Exception as error:
                if isinstance(error, RuntimeFoundationError):
                    sys.stderr.write(f"Runtime cleanup failed: {error}\n")
                    failure = failure or str(error)
                elif protected_route and primary is not None:
                    primary.add_note("An unexpected runtime cleanup failure occurred.")
                else:
                    raise
    if failure is not None:
        sys.stderr.write(f"Publication failed: {failure}\n")
        return 1
    assert result is not None
    sys.stdout.write(f"Published: {result.output}\n")
    return 0
