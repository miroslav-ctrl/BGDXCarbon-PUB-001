"""TOC targets, Unicode, duplicate collisions and CLI compatibility."""

import re
from pathlib import Path
from urllib.parse import unquote

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.publishing.renderer import HtmlRenderer


def test_toc_is_opt_in_and_no_headings_leave_output_unchanged() -> None:
    renderer = HtmlRenderer()
    plain = renderer.render("# Header", "Title")
    assert "<nav" not in plain and " id=" not in plain
    assert plain == renderer.render("# Header", "Title", toc=False)
    assert renderer.render("Paragraph", "Title") == renderer.render(
        "Paragraph", "Title", toc=True
    )


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_toc_links_have_unique_heading_targets(theme: str) -> None:
    source = (
        "# Čćšžđ\n\n## Ћирилица\n\n## Repeat\n\n## Repeat\n\n## Repeat 2\n\n"
        "### Repeat\n\n#### !!!\n\n#####\n\n###### Last\n\nSetext\n======\n"
    )
    html = HtmlRenderer().render(source, "Report & title", "sr-Latn", theme, True)
    nav, body = html.partition("</nav>")[0], html.partition("</nav>")[2]
    ids = re.findall(r'<h[1-6] id="([^"]+)"', body)
    links = [unquote(value) for value in re.findall(r'href="#([^"]+)"', nav)]
    assert links == ids
    assert len(ids) == len(set(ids)) == 10
    assert ids[:6] == [
        "section-čćšžđ",
        "section-ћирилица",
        "section-repeat",
        "section-repeat-2",
        "section-repeat-2-2",
        "section-repeat-3",
    ]
    assert "section-heading" in ids
    assert "Untitled section" in nav
    assert "toc-level-6" in nav
    assert "<title>Report &amp; title</title>" in html
    assert '<html lang="sr-Latn">' in html
    assert f"color-scheme:{theme}" in html
    assert 'lang="en"' in nav


def test_toc_labels_strip_formatting_and_escape_html() -> None:
    source = (
        "# **bold** `code` [link](https://example.com) "
        "![alt](custom:image) & <script>\n"
    )
    html = HtmlRenderer().render(source, "Title", toc=True)
    nav = html.partition("</nav>")[0].partition("<nav")[2]
    assert "bold code link alt &amp; &lt;script&gt;</a>" in nav
    assert "<script>" not in html
    assert 'href="https:' not in nav
    assert "<img" not in html
    assert "**" not in nav and "`" not in nav


def test_canonically_equivalent_headings_get_unique_ids() -> None:
    html = HtmlRenderer().render("# Café\n\n# Cafe\u0301", "Title", toc=True)
    assert '<h1 id="section-café">' in html
    assert '<h1 id="section-café-2">' in html


def test_code_block_headings_are_not_indexed() -> None:
    html = HtmlRenderer().render("```\n# Fake\n```\n\n## Real", "Title", toc=True)
    nav = html.partition("</nav>")[0].partition("<nav")[2]
    assert "Real</a>" in nav and "Fake</a>" not in nav


def test_cli_toc_preserves_input_and_overwrite_contract(tmp_path: Path) -> None:
    source = tmp_path / "sample.md"
    source.write_text("# First\n\n## Second", encoding="utf-8-sig")
    before = source.read_bytes()
    output = tmp_path / "result.html"
    args = ["publish", str(source), "--output", str(output), "--toc", "--theme", "dark"]
    assert main(args) == 0
    html = output.read_text(encoding="utf-8")
    assert '<nav class="toc"' in html
    assert 'href="#section-second"' in html
    assert source.read_bytes() == before
    assert main(args) == 1
    assert output.read_text(encoding="utf-8") == html
    assert main([*args, "--overwrite"]) == 0


def test_large_duplicate_heading_index_has_linear_lookup_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import bgdxpublisher.publishing.toc as module

    class CountingSet(set[str]):
        lookups = 0

        def __contains__(self, value: object) -> bool:
            type(self).lookups += 1
            return super().__contains__(value)

    monkeypatch.setattr(module, "set", CountingSet, raising=False)
    count = 5000
    html = HtmlRenderer().render("## Repeat\n\n" * count, "Title", toc=True)
    ids = re.findall(r'<h2 id="(section-[^"]+)"', html)
    links = re.findall(r'href="#(section-[^"]+)"', html)
    assert len(ids) == len(set(ids)) == count
    assert links == ids
    assert ids[0] == "section-repeat"
    assert ids[-1] == f"section-repeat-{count}"
    assert CountingSet.lookups <= 3 * count
