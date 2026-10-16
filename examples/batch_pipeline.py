"""Installed-wheel batch API smoke with independent index failure."""

import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from bgdxpublisher.batch_pipeline import BatchHtmlPublicationService
from bgdxpublisher.html_pipeline import HtmlPublicationService
from bgdxpublisher.jobs import JobStatus
from bgdxpublisher.publishing.batch import BatchRequest


def main() -> None:
    """Verify complete success, partial failure and index revalidation."""
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "source"
        source.mkdir()
        (source / "a.md").write_text("# Čć Ћирилица", encoding="utf-8-sig")
        (source / "b.md").write_text("# B", encoding="utf-8")
        logger = logging.getLogger("batch-example")
        result = BatchHtmlPublicationService(logger).publish(
            BatchRequest(source, root / "good", index=True)
        )
        assert all(
            p.execution.final_job.status is JobStatus.COMPLETED for p in result.items
        )
        assert result.index is not None
        (source / "b.md").write_bytes(b"\xff")
        result = BatchHtmlPublicationService(logger).publish(
            BatchRequest(source, root / "partial", index=True)
        )
        assert result.items[1].execution.final_job.status is JobStatus.FAILED
        assert result.index is not None
        assert "b.html" not in result.index.output.read_text(encoding="utf-8")

        class IndexRacePublisher(HtmlPublicationService):
            def publish(self, request):
                result = super().publish(request)
                (request.output.parent / "index.html").write_text("competitor")
                return result

        result = BatchHtmlPublicationService(
            logger, IndexRacePublisher(logger)
        ).publish(BatchRequest(source, root / "race", index=True))
        assert result.index is None and result.index_failure is not None
        assert result.index_failure.code == "BATCH_INDEX_FAILED"
        assert result.items[0].output.exists()


if __name__ == "__main__":
    main()
