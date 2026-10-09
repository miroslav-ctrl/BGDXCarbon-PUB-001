"""HTML metadata validation and publication regressions."""

import logging
from pathlib import Path

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.publishing import PublishingError, PublishingService, PublishRequest
from bgdxpublisher.publishing.renderer import HtmlRenderer


@pytest.mark.parametrize(
    "language",
    ["und", "sr", "sr-Latn", "sr-Cyrl-RS", "en-US", "es-419", "sl-rozaj", "de-CH-1901"],
)
def test_language_and_escaped_title(language: str) -> None:
    html = HtmlRenderer().render("# Body", 'Čć </title><script> & "quoted"', language)
    assert f'<html lang="{language}">' in html
    assert (
        "<title>Čć &lt;/title&gt;&lt;script&gt; &amp; &quot;quoted&quot;</title>"
        in html
    )
    assert "<h1>Body</h1>" in html
    assert "<script>" not in html


@pytest.mark.parametrize(
    "title,language",
    [
        ("", "en"),
        ("  ", "sr"),
        ("one\ntwo", "en"),
        ("one\x00two", "en"),
        ("one\u2028two", "en"),
        ("Title", ""),
        ("Title", "en_US"),
        ("Title", 'en" onclick="evil'),
        ("Title", "en-x"),
        ("Title", "123"),
        ("Title", " en "),
    ],
)
def test_invalid_metadata_preserves_existing_output(
    tmp_path: Path, title: str, language: str
) -> None:
    source = tmp_path / "source.md"
    source.write_text("# Body", encoding="utf-8")
    output = tmp_path / "out.html"
    output.write_text("original", encoding="utf-8")
    with pytest.raises(PublishingError):
        PublishingService(logging.getLogger("test.metadata")).publish(
            PublishRequest(source, output, True, title, language)
        )
    assert output.read_bytes() == b"original"
    assert source.read_bytes() == b"# Body"
    assert not list(tmp_path.glob(".bgdx-*.tmp"))


def test_cli_metadata_and_defaults(tmp_path: Path) -> None:
    source = tmp_path / "document.md"
    source.write_text("# Heading", encoding="utf-8-sig")
    output = tmp_path / "out.html"
    assert main(["publish", str(source), "--output", str(output)]) == 0
    html = output.read_text(encoding="utf-8")
    assert "<title>document</title>" in html
    assert '<html lang="und">' in html
    assert (
        main(
            [
                "publish",
                str(source),
                "--output",
                str(output),
                "--overwrite",
                "--title",
                "Izveštaj & pregled",
                "--lang",
                "sr-Latn",
            ]
        )
        == 0
    )
    html = output.read_text(encoding="utf-8")
    assert "<title>Izveštaj &amp; pregled</title>" in html
    assert '<html lang="sr-Latn">' in html
    assert "<h1>Heading</h1>" in html


@pytest.mark.parametrize(
    "option,value",
    [
        ("--title", " "),
        ("--title", "a\nb"),
        ("--lang", "en_US"),
        ("--lang", "<script>"),
    ],
)
def test_cli_rejects_invalid_metadata_before_publication(
    tmp_path: Path, option: str, value: str
) -> None:
    output = tmp_path / "out.html"
    with pytest.raises(SystemExit) as error:
        main(["publish", "missing.md", "--output", str(output), option, value])
    assert error.value.code == 2
    assert not output.exists()
