"""Direct legacy batch API keeps its raw diagnostic/result contracts."""

import logging

from bgdxpublisher.publishing import PublishingService
from bgdxpublisher.publishing.batch import BatchRequest, publish_batch


def test_direct_partial_failure_preserves_raw_diagnostic(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.md").write_bytes(b"\xff")
    (source / "b.md").write_text("# B", encoding="utf-8")
    result = publish_batch(
        PublishingService(logging.getLogger("legacy")),
        BatchRequest(source, tmp_path / "out", index=True),
    )
    assert result.items[0].error is not None
    assert "utf-8" in result.items[0].error
    assert result.items[1].error is None
    assert result.index is not None and result.index_error is None
