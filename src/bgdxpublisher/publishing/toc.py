"""Build an optional escaped index from parsed Markdown headings."""

import unicodedata
from collections.abc import Callable
from html import escape
from urllib.parse import quote

from markdown_it.token import Token

TOC_CSS = (
    ".toc{border:1px solid currentColor;padding:16px 24px;margin-bottom:32px}"
    ".toc ol{list-style:none;padding:0}.toc li{margin:6px 0}"
    ".toc-level-2{padding-left:16px}.toc-level-3{padding-left:32px}"
    ".toc-level-4{padding-left:48px}.toc-level-5{padding-left:64px}"
    ".toc-level-6{padding-left:80px}"
)


def build_toc(tokens: list[Token], plain_text: Callable[[list[Token]], str]) -> str:
    """Assign unique h1–h6 IDs and return an index in document order."""
    used: set[str] = set()
    next_suffix: dict[str, int] = {}
    entries = []
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        label = plain_text(tokens[index + 1].children or []).strip()
        label = label or "Untitled section"
        normalized = unicodedata.normalize("NFC", label).casefold()
        words = "".join(c if c.isalnum() else " " for c in normalized).split()
        slug = "-".join(words)
        base = "section-" + (slug or "heading")
        identifier = base
        suffix = next_suffix.get(base, 2)
        while identifier in used:
            identifier = f"{base}-{suffix}"
            suffix += 1
        used.add(identifier)
        next_suffix[base] = suffix
        token.attrSet("id", identifier)
        destination = quote(identifier, safe="")
        entries.append(
            f'<li class="toc-level-{token.tag[1:]}"><a href="#{destination}">'
            f"{escape(label)}</a></li>\n"
        )
    if not entries:
        return ""
    return (
        '<nav class="toc" aria-labelledby="toc-title">\n'
        '<h2 id="toc-title" lang="en">Contents</h2>\n<ol>\n'
        + "".join(entries)
        + "</ol>\n</nav>\n"
    )
