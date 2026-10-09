"""Render Markdown as a self-contained HTML document."""

from html import escape
from urllib.parse import urlsplit

from markdown_it import MarkdownIt
from markdown_it.rules_inline.image import image
from markdown_it.rules_inline.state_inline import StateInline
from markdown_it.token import Token


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

    def render(self, source: str, title: str) -> str:
        """Return UTF-8-ready HTML; unsafe link destinations remain plain text."""
        parser = _SafeMarkdown("commonmark", {"html": False})
        parser.inline.ruler.at("image", _image_as_text)
        tokens = parser.parse(source)
        _remove_images(tokens)
        body = parser.renderer.render(tokens, parser.options, {})
        return (
            '<!doctype html>\n<html lang="und">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta http-equiv="Content-Security-Policy" '
            "content=\"default-src 'none'; style-src 'unsafe-inline'; "
            "base-uri 'none'; form-action 'none'\">\n"
            f"<title>{escape(title)}</title>\n"
            "<style>body{font:18px/1.65 system-ui,sans-serif;max-width:"
            "760px;margin:48px auto;padding:0 24px;color:#202630}"
            "h1,h2,h3{line-height:1.2}a{color:#1659a5}pre{overflow:auto;"
            "padding:18px;background:#f1f3f5;border-radius:6px}"
            "code{font-family:monospace}blockquote{border-left:3px solid "
            "#aab4c0;margin-left:0;padding-left:20px}</style>\n"
            f"</head>\n<body>\n<main>\n{body}</main>\n</body>\n</html>\n"
        )
