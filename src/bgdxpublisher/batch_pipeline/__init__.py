"""Sequential batch HTML publication with independent job outcomes."""

from .service import (
    BatchHtmlItem,
    BatchHtmlPublicationError,
    BatchHtmlPublicationResult,
    BatchHtmlPublicationService,
    BatchIndexFailure,
)

__all__ = [
    "BatchHtmlItem",
    "BatchHtmlPublicationError",
    "BatchHtmlPublicationResult",
    "BatchHtmlPublicationService",
    "BatchIndexFailure",
]
