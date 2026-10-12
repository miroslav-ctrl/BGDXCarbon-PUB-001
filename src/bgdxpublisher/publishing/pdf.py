"""Publish portable PDF documents directly from safe CommonMark tokens."""

import logging
import unicodedata
from dataclasses import dataclass
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit

from markdown_it.token import Token
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from reportlab.platypus import Flowable, HRFlowable, Paragraph, SimpleDocTemplate
from reportlab.platypus.doctemplate import LayoutError

from .metadata import validate_language, validate_title
from .renderer import _image_as_text, _remove_images, _SafeMarkdown
from .service import PublishingError, PublishingService, PublishResult

_FONT_FILES = {
    "BGDXSans": "DejaVuSans.ttf",
    "BGDXSans-Bold": "DejaVuSans-Bold.ttf",
    "BGDXSans-Italic": "DejaVuSans-Oblique.ttf",
    "BGDXSans-BoldItalic": "DejaVuSans-BoldOblique.ttf",
    "BGDXMono": "DejaVuSansMono.ttf",
}


def _register_fonts() -> None:
    """Load licensed package fonts, never operating-system fonts."""
    directory = Path(__file__).with_name("fonts")
    for name, filename in _FONT_FILES.items():
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(directory / filename)))
    pdfmetrics.registerFontFamily(
        "BGDXSans",
        normal="BGDXSans",
        bold="BGDXSans-Bold",
        italic="BGDXSans-Italic",
        boldItalic="BGDXSans-BoldItalic",
    )
    pdfmetrics.registerFontFamily(
        "BGDXMono",
        normal="BGDXMono",
        bold="BGDXMono",
        italic="BGDXMono",
        boldItalic="BGDXMono",
    )


def _text(value: str, font: str) -> str:
    """Reject missing glyphs and XML controls rather than silently losing text."""
    glyphs = pdfmetrics.getFont(font).face.charToGlyph
    for character in value:
        if character in "\n\t\r":
            continue
        if unicodedata.category(character) == "Cc" or ord(character) not in glyphs:
            raise ValueError(
                f"PDF font cannot render character U+{ord(character):04X}."
            )
    return escape(value, quote=True)


def _inline(tokens: list[Token], heading: bool = False) -> str:
    """Generate renderer-owned paragraph markup; raw source is always escaped."""
    parts = []
    bold = int(heading)
    italic = 0
    active_link = False
    for token in tokens:
        if token.type == "strong_open":
            bold += 1
            parts.append("<b>")
        elif token.type == "strong_close":
            bold -= 1
            parts.append("</b>")
        elif token.type == "em_open":
            italic += 1
            parts.append("<i>")
        elif token.type == "em_close":
            italic -= 1
            parts.append("</i>")
        elif token.type == "link_open":
            href = str(token.attrGet("href") or "")
            active_link = urlsplit(href).scheme.lower() in ("http", "https", "mailto")
            if active_link:
                parts.append(
                    f'<a href="{escape(href, quote=True)}" color="#0563c1"><u>'
                )
        elif token.type == "link_close":
            if active_link:
                parts.append("</u></a>")
            active_link = False
        elif token.type in ("softbreak", "hardbreak"):
            parts.append(" " if token.type == "softbreak" else "<br/>")
        elif token.type == "code_inline":
            parts.append(
                f'<font name="BGDXMono">{_text(token.content, "BGDXMono")}</font>'
            )
        else:
            font = (
                "BGDXSans-BoldItalic"
                if bold and italic
                else (
                    "BGDXSans-Bold"
                    if bold
                    else "BGDXSans-Italic" if italic else "BGDXSans"
                )
            )
            parts.append(_text(token.content, font))
    return "".join(parts)


@dataclass(frozen=True, slots=True)
class PdfRequest:
    """Paths, explicit overwrite policy and PDF document metadata."""

    source: Path
    output: Path
    overwrite: bool = False
    title: str | None = None
    language: str = "und"


class PdfRenderer:
    """Render A4 pages with embedded Latin/Cyrillic fonts and active safe links."""

    def render(self, source: str, title: str, language: str = "und") -> bytes:
        """Return PDF bytes with automatic pagination and selectable text."""
        validate_title(title)
        validate_language(language)
        _register_fonts()
        parser = _SafeMarkdown("commonmark", {"html": False})
        parser.inline.ruler.at("image", _image_as_text)
        tokens = parser.parse(source)
        _remove_images(tokens)
        story: list[Flowable] = []
        lists: list[tuple[bool, int, bool]] = []
        quotes = heading = 0
        for token in tokens:
            if token.type == "heading_open":
                heading = int(token.tag[1:])
            elif token.type == "heading_close":
                heading = 0
            elif token.type == "blockquote_open":
                quotes += 1
            elif token.type == "blockquote_close":
                quotes -= 1
            elif token.type in ("bullet_list_open", "ordered_list_open"):
                lists.append(
                    (
                        token.type == "ordered_list_open",
                        int(token.attrGet("start") or 1),
                        False,
                    )
                )
            elif token.type in ("bullet_list_close", "ordered_list_close"):
                lists.pop()
            elif token.type == "list_item_open":
                ordered, number, _ = lists[-1]
                lists[-1] = (ordered, number, True)
            elif token.type in ("inline", "fence", "code_block", "hr"):
                indent = 0.7 * cm * (len(lists) + quotes)
                bullet_indent = max(0, indent - 0.5 * cm)
                if lists:
                    ordered, number, pending = lists[-1]
                    current_number = number if pending else number - 1
                    label = f"{current_number}." if ordered else "•"
                    indent = max(
                        indent,
                        bullet_indent
                        + pdfmetrics.stringWidth(label, "BGDXSans", 11)
                        + 8,
                    )
                right_indent = 0.7 * cm * quotes
                if indent + right_indent > 12 * cm:
                    raise ValueError("PDF nesting is too deep for the page width.")
                marker = None
                if lists and lists[-1][2]:
                    ordered, number, _ = lists[-1]
                    marker = f"{number}." if ordered else "•"
                    lists[-1] = (ordered, number + 1, False)
                if token.type == "hr":
                    story.append(
                        HRFlowable(
                            width="100%", thickness=0.5, spaceBefore=8, spaceAfter=8
                        )
                    )
                    continue
                code = token.type != "inline"
                size = (
                    10
                    if code
                    else (22, 17, 14, 12, 11, 11)[heading - 1] if heading else 11
                )
                style = ParagraphStyle(
                    "block",
                    fontName=(
                        "BGDXMono"
                        if code
                        else "BGDXSans-Bold" if heading else "BGDXSans"
                    ),
                    fontSize=size,
                    leading=size * 1.35,
                    spaceAfter=8,
                    spaceBefore=12 if heading else 0,
                    leftIndent=indent,
                    rightIndent=right_indent,
                    bulletIndent=bullet_indent,
                    bulletFontName="BGDXSans",
                    bulletFontSize=11,
                    keepWithNext=bool(heading),
                    splitLongWords=True,
                )
                if code:
                    markup = "<br/>".join(
                        _text(line, "BGDXMono").replace(" ", "&#160;") or "&#160;"
                        for line in token.content.rstrip("\n").expandtabs(4).split("\n")
                    )
                else:
                    markup = _inline(token.children or [], bool(heading)) or "&#160;"
                story.append(Paragraph(markup, style, bulletText=marker))
        if not story:
            story.append(
                Paragraph("&#160;", ParagraphStyle("empty", fontName="BGDXSans"))
            )
        stream = BytesIO()
        document = SimpleDocTemplate(
            stream,
            pagesize=A4,
            leftMargin=2.5 * cm,
            rightMargin=2.5 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2.5 * cm,
            title=title,
            author="",
            lang=language,
            pageCompression=1,
        )
        document.build(story)
        return stream.getvalue()


class PdfPublishingService:
    """Read UTF-8 Markdown and atomically commit a PDF output."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def publish(self, request: PdfRequest) -> PublishResult:
        """Preserve source and previous output on expected publication failure."""
        try:
            source = request.source.resolve(strict=True)
            output = request.output.absolute()
            if source == output.resolve() or (
                output.exists() and source.samefile(output)
            ):
                raise PublishingError("Input and output must be different files.")
            if not source.is_file():
                raise PublishingError("Input must be a regular file.")
            if output.suffix.lower() != ".pdf":
                raise PublishingError("PDF output must have a .pdf extension.")
            PublishingService.validate_output(output, request.overwrite)
            content = PdfRenderer().render(
                source.read_text(encoding="utf-8-sig"),
                source.stem if request.title is None else request.title,
                request.language,
            )
            PublishingService.write_bytes(output, content, request.overwrite)
        except (OSError, UnicodeError, ValueError, LayoutError, TTFError) as error:
            raise PublishingError(f"Unable to publish PDF: {error}") from error
        self._logger.info("Published PDF: %s", output)
        return PublishResult(output, len(content))
