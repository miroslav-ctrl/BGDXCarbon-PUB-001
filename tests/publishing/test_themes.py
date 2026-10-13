"""Theme selection preserves content, security and output safety."""

import logging
from pathlib import Path

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.publishing import PublishingError, PublishingService, PublishRequest
from bgdxpublisher.publishing.renderer import HtmlRenderer


def test_default_theme_matches_explicit_light() -> None:
    renderer = HtmlRenderer()
    assert renderer.render("# Body", "Title") == renderer.render(
        "# Body", "Title", theme="light"
    )


@pytest.mark.parametrize(
    "theme,background,foreground,link,code,border",
    [
        ("light", "#ffffff", "#202630", "#1659a5", "#f1f3f5", "#aab4c0"),
        ("dark", "#161b22", "#e6edf3", "#79c0ff", "#242c36", "#8b949e"),
    ],
)
def test_theme_palette_and_preserved_content(
    theme: str, background: str, foreground: str, link: str, code: str, border: str
) -> None:
    source = (
        "# Čć / Ћирилица\n\n[link](https://example.com)\n\n> Quote\n\n"
        "```\ncode\n```\n\n<script>bad</script>"
    )
    renderer = HtmlRenderer()
    html = renderer.render(source, "Title & report", "sr-Latn", theme)
    assert f"html{{background:{background};color-scheme:{theme}}}" in html
    assert f"color:{foreground}" in html
    assert f"a{{color:{link}}}" in html
    assert f"background:{code}" in html
    assert f"border-left:3px solid {border}" in html
    assert "<title>Title &amp; report</title>" in html
    assert '<html lang="sr-Latn">' in html
    assert "default-src 'none'" in html
    assert "<script>" not in html
    assert "&lt;script&gt;bad&lt;/script&gt;" in html
    other = renderer.render(
        source, "Title & report", "sr-Latn", "light" if theme == "dark" else "dark"
    )
    assert html.partition("<main>")[2] == other.partition("<main>")[2]


@pytest.mark.parametrize("theme", ["dark", "light"])
def test_cli_theme_and_overwrite(tmp_path: Path, theme: str) -> None:
    source = tmp_path / "source.md"
    source.write_text("# Body", encoding="utf-8-sig")
    output = tmp_path / "out.html"
    output.write_text("old", encoding="utf-8")
    arguments = [
        "publish",
        str(source),
        "--output",
        str(output),
        "--theme",
        theme,
        "--title",
        "Report",
        "--lang",
        "en",
    ]
    assert main(arguments) == 1
    assert output.read_bytes() == b"old"
    assert main([*arguments, "--overwrite"]) == 0
    html = output.read_text(encoding="utf-8")
    assert f"color-scheme:{theme}" in html
    assert "<title>Report</title>" in html
    assert '<html lang="en">' in html
    assert "<h1>Body</h1>" in html
    assert source.read_text(encoding="utf-8-sig") == "# Body"


@pytest.mark.parametrize("theme", ["", "blue", "Dark", "</style><script>"])
def test_invalid_service_theme_preserves_output(tmp_path: Path, theme: str) -> None:
    source = tmp_path / "source.md"
    source.write_text("content", encoding="utf-8")
    output = tmp_path / "out.html"
    output.write_text("old", encoding="utf-8")
    with pytest.raises(PublishingError, match="Theme must be light or dark"):
        PublishingService(logging.getLogger("test.themes")).publish(
            PublishRequest(source, output, True, theme=theme)
        )
    assert output.read_bytes() == b"old"
    assert source.read_bytes() == b"content"
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


def test_invalid_cli_theme_has_useful_diagnostic(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "out.html"
    with pytest.raises(SystemExit) as error:
        main(["publish", "missing.md", "--output", str(output), "--theme", "blue"])
    assert error.value.code == 2
    diagnostic = capsys.readouterr().err
    assert "--theme" in diagnostic and "light" in diagnostic and "dark" in diagnostic
    assert not output.exists()
