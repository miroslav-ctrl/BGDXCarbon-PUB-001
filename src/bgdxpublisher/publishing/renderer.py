"""Render Markdown as a self-contained HTML document."""

from html import escape
from urllib.parse import urlsplit

from markdown_it import MarkdownIt
from markdown_it.rules_inline.image import image
from markdown_it.rules_inline.state_inline import StateInline
from markdown_it.token import Token

from .metadata import validate_language, validate_title
from .themes import theme_css
from .toc import TOC_CSS, build_toc


class _SafeMarkdown(MarkdownIt):
    """Also reject data URLs, including the parser's default image exceptions."""

    parsing_image = False

    def validateLink(self, url: str) -> bool:
        if self.parsing_image:
            return True
        return urlsplit(url).scheme.lower() in (
            "",
            "http",
            "https",
            "mailto",
        ) and super().validateLink(url)


def _image_as_text(state: StateInline, silent: bool) -> bool:
    """Parse image labels even for rejected destinations; images are removed."""
    parser = state.md
    assert isinstance(parser, _SafeMarkdown)
    previous = parser.parsing_image
    parser.parsing_image = True
    try:
        return image(state, silent)
    finally:
        parser.parsing_image = previous


def _plain_label(tokens: list[Token]) -> str:
    """Keep label content while discarding formatting and link destinations."""
    parts = []
    for token in tokens:
        if token.type in ("text", "text_special", "code_inline"):
            parts.append(token.content)
        elif token.type in ("softbreak", "hardbreak"):
            parts.append("\n")
        elif token.children:
            parts.append(_plain_label(token.children))
    return "".join(parts)


def _remove_images(tokens: list[Token]) -> None:
    """Replace images with escaped alternative text, without network requests."""
    for token in tokens:
        if token.type == "image":
            token.content = _plain_label(token.children or [])
            token.type = "text"
            token.tag = ""
            token.attrs = {}
            token.children = None
        elif token.children:
            _remove_images(token.children)


class HtmlRenderer:
    """Render supported Markdown without raw HTML or external images."""

    def render(
        self,
        source: str,
        title: str,
        language: str = "und",
        theme: str = "light",
        toc: bool = False,
    ) -> str:
        """Return UTF-8-ready HTML; unsafe link destinations remain plain text."""
        validate_title(title)
        validate_language(language)
        styles = theme_css(theme)
        parser = _SafeMarkdown("commonmark", {"html": False})
        parser.inline.ruler.at("image", _image_as_text)
        tokens = parser.parse(source)
        _remove_images(tokens)
        contents = build_toc(tokens, _plain_label) if toc else ""
        if contents:
            styles += TOC_CSS
        body = parser.renderer.render(tokens, parser.options, {})
        return (
            f'<!doctype html>\n<html lang="{escape(language, quote=True)}">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta http-equiv="Content-Security-Policy" '
            "content=\"default-src 'none'; style-src 'unsafe-inline'; "
            "base-uri 'none'; form-action 'none'\">\n"
            f"<title>{escape(title)}</title>\n"
            f"<style>{styles}</style>\n"
            f"</head>\n<body>\n<main>\n{contents}{body}</main>\n</body>\n</html>\n"
        )
