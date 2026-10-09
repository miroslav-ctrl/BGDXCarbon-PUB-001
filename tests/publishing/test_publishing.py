"""Publication contracts, security and filesystem failures."""

import logging
import os
from pathlib import Path

import pytest

from bgdxpublisher.publishing import PublishingError, PublishingService, PublishRequest
from bgdxpublisher.publishing.renderer import HtmlRenderer


def service() -> PublishingService:
    return PublishingService(logging.getLogger("test.publisher"))


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_publish_utf8_heading_with_optional_bom(tmp_path: Path, encoding: str) -> None:
    source = tmp_path / "document.md"
    source.write_text("# SPR-003 provera\n\nČćšžđ — Ћирилица.", encoding=encoding)
    original = source.read_bytes()
    output = tmp_path / "document.html"

    service().publish(PublishRequest(source, output))

    html = output.read_text(encoding="utf-8")
    assert "<h1>SPR-003 provera</h1>" in html
    assert "Čćšžđ — Ћирилица." in html
    assert "\ufeff" not in html
    assert not output.read_bytes().startswith(b"\xef\xbb\xbf")
    assert source.read_bytes() == original


def test_render_unicode_and_markdown() -> None:
    html = HtmlRenderer().render(
        "# Zdravo / Здраво\n\n**bold** *italic* [link](https://example.com)\n"
        "\n- one\n- two\n\n1. first\n\n```python\nprint('<')\n```\n",
        "<Title>",
    )
    for expected in [
        "<h1>Zdravo / Здраво</h1>",
        "<strong>bold</strong>",
        '<a href="https://example.com">link</a>',
        "<em>italic</em>",
        "<ul>",
        "<ol>",
        "<pre><code",
        "&lt;Title&gt;",
        'charset="utf-8"',
        "<p>",
    ]:
        assert expected in html


@pytest.mark.parametrize(
    "text",
    [
        "<script>alert(1)</script>",
        "[x](javascript:alert%281%29)",
        "[x](vbscript:run)",
        "[x](data:text/html,evil)",
        "[x](file:///secret)",
        "[x](custom:payload)",
        "![x](https://example.com/tracking.png)",
        "![x](data:image/png;base64,a)",
    ],
)
def test_unsafe_html_links_and_images_are_inert(text: str) -> None:
    html = HtmlRenderer().render(text, "test")
    assert "<script" not in html
    assert "<img" not in html
    assert "href=" not in html
    assert "default-src 'none'" in html
    body = html.partition("<main>\n")[2].partition("</main>")[0]
    if text.startswith("<script>"):
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
    elif text.startswith("![x](https:"):
        assert "<p>x</p>" in body
    else:
        assert text in body


def test_publish_and_overwrite(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    source = tmp_path / "srpski.md"
    source.write_text("# Čćšžđ / Ћирилица", encoding="utf-8")
    original = source.read_bytes()
    output = tmp_path / "result.html"
    with caplog.at_level(logging.INFO):
        result = service().publish(PublishRequest(source, output))
    assert result.output == output
    assert result.bytes_written == len(output.read_bytes())
    assert "Ћирилица" in output.read_text(encoding="utf-8")
    assert "Publishing document" in caplog.text
    assert "Published document" in caplog.text
    source.write_text("new", encoding="utf-8")
    with pytest.raises(PublishingError, match="--overwrite"):
        service().publish(PublishRequest(source, output))
    assert "Ћирилица" in output.read_text(encoding="utf-8")
    source.write_bytes(original)
    service().publish(PublishRequest(source, output, True))
    assert source.read_bytes() == original
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "directory",
        "same",
        "hardlink",
        "invalid_utf8",
        "output_directory",
        "no_parent",
    ],
)
def test_invalid_paths_and_encoding_preserve_output(tmp_path: Path, case: str) -> None:
    source = tmp_path / "source.md"
    source.write_text("hello", encoding="utf-8")
    output = tmp_path / "out.html"
    output.write_text("original", encoding="utf-8")
    if case == "missing":
        source = tmp_path / "missing.md"
    elif case == "directory":
        source = tmp_path
    elif case == "same":
        output = source
    elif case == "hardlink":
        output.unlink()
        os.link(source, output)
    elif case == "invalid_utf8":
        source.write_bytes(b"\xff")
    elif case == "output_directory":
        output = tmp_path
    elif case == "no_parent":
        output = tmp_path / "missing" / "out.html"
    before = output.read_bytes() if output.is_file() else None
    with pytest.raises(PublishingError):
        service().publish(PublishRequest(source, output, True))
    if before is not None:
        assert output.read_bytes() == before
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


@pytest.mark.parametrize("stage", ["read", "render", "flush", "commit"])
def test_failure_preserves_previous_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str
) -> None:
    source = tmp_path / "source.md"
    source.write_text("hello", encoding="utf-8")
    output = tmp_path / "out.html"
    output.write_text("original", encoding="utf-8")

    def fail(*args: object, **kwargs: object) -> None:
        raise OSError("simulated failure")

    if stage == "read":
        monkeypatch.setattr(Path, "read_text", fail)
    elif stage == "render":
        monkeypatch.setattr(HtmlRenderer, "render", fail)
    elif stage == "flush":
        monkeypatch.setattr(os, "fsync", fail)
    else:
        monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(PublishingError, match="simulated failure"):
        service().publish(PublishRequest(source, output, True))
    assert output.read_bytes() == b"original"
    assert source.read_bytes() == b"hello"
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


def test_concurrent_output_creation_is_not_overwritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.md"
    source.write_text("hello", encoding="utf-8")
    output = tmp_path / "out.html"
    original_link = os.link

    def race(src: Path, dst: Path) -> None:
        dst.write_text("other writer", encoding="utf-8")
        original_link(src, dst)

    monkeypatch.setattr(os, "link", race)
    with pytest.raises(PublishingError):
        service().publish(PublishRequest(source, output))
    assert output.read_text(encoding="utf-8") == "other writer"
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


def test_symbolic_output_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source.md"
    source.write_text("hello", encoding="utf-8")
    output = tmp_path / "out.html"
    monkeypatch.setattr(Path, "is_symlink", lambda self: self == output)
    with pytest.raises(PublishingError, match="symbolic"):
        service().publish(PublishRequest(source, output, True))
