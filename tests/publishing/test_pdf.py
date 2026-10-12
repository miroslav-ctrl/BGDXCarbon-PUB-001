"""Validate portable PDF content, metadata, link safety and file contracts."""

import logging
from io import BytesIO
from pathlib import Path

import pytest
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError
from reportlab.platypus.doctemplate import LayoutError

from bgdxpublisher.cli.app import main
from bgdxpublisher.publishing.pdf import PdfPublishingService, PdfRenderer, PdfRequest
from bgdxpublisher.publishing.service import PublishingError, PublishingService
from bgdxpublisher.runtime import PublisherApplication, RuntimeState


def _read(source: str, title: str = "Izveštaj", language: str = "sr-Latn") -> PdfReader:
    return PdfReader(BytesIO(PdfRenderer().render(source, title, language)))


def test_pdf_unicode_structure_and_embedded_fonts() -> None:
    doc = _read(
        "# Čćšžđ Ћирилица\n\n## Heading two\n\n### Three\n\n"
        "#### Four\n\n##### Five\n\n###### Six\n\n"
        "Plain **bold**, *italic*, ***both***, and `code`.\nsoft  \nhard\n\n"
        "- First\n  - Nested\n- Second\n\n3. Third\n4. Fourth\n\nSeparate\n\n"
        "1. First again\n2. Second again\n\n> Quote\n>\n> More\n\n"
        '```python\nprint("Здраво")\n    indented\n```\n\n    plain code\n\n---\n'
    )
    text = "".join(page.extract_text() for page in doc.pages)
    for expected in (
        "Čćšžđ Ћирилица",
        "Heading two",
        "Three",
        "Four",
        "Five",
        "Six",
        "bold",
        "italic",
        "both",
        "code",
        "Nested",
        "Quote",
        "More",
        'print("Здраво")',
        "indented",
        "plain code",
        "First again",
    ):
        assert expected in text
    assert "3." in text and "4." in text and "1." in text and "2." in text
    assert doc.metadata.title == "Izveštaj"
    assert doc.trailer["/Root"]["/Lang"] == "sr-Latn"
    page = doc.pages[0]
    assert float(page.mediabox.width) == pytest.approx(595.28, abs=0.02)
    assert float(page.mediabox.height) == pytest.approx(841.89, abs=0.02)
    fonts = [font.get_object() for font in page["/Resources"]["/Font"].values()]
    embedded = [font for font in fonts if "/FontDescriptor" in font]
    assert len(embedded) == 5
    assert all("/FontFile2" in font["/FontDescriptor"] for font in embedded)
    assert all("/ToUnicode" in font for font in embedded)


def test_pdf_safe_links_and_visible_fallbacks() -> None:
    doc = _read(
        "[**Safe**](https://example.com?q=1&b=2) [email](mailto:a@example.com) "
        "[web](http://example.com) [local](other.md) [jump](#heading) "
        "[unsafe](javascript:alert(1)) <script>alert(1)</script> "
        "![**Formatted** `alt`](data:image/png;base64,x)"
    )
    text = "".join(page.extract_text() for page in doc.pages)
    assert "Safe" in text and "local" in text and "jump" in text
    assert "Formatted alt" in text and "<script>alert(1)</script>" in text
    assert "unsafe" in text
    actions = [
        annotation.get_object()["/A"]
        for page in doc.pages
        for annotation in page.get("/Annots", [])
    ]
    assert [a["/URI"] for a in actions] == [
        "https://example.com?q=1&b=2",
        "mailto:a@example.com",
        "http://example.com",
    ]
    assert all(a["/S"] == "/URI" for a in actions)
    assert (
        "/JavaScript" not in doc.trailer["/Root"]
        and "/OpenAction" not in doc.trailer["/Root"]
    )
    assert "/XObject" not in doc.pages[0]["/Resources"]


@pytest.mark.parametrize(
    "source", ["", "\n", "- \n", "> > Nested\n", "- # Heading\n- ```\n  code\n  ```\n"]
)
def test_empty_and_compound_markdown(source: str) -> None:
    assert len(_read(source).pages) >= 1


def test_automatic_pagination_and_long_code() -> None:
    source = "# Long report\n\n" + "\n\n".join(
        f"Paragraph {i}: Čćšžđ Ћирилица " * 4 for i in range(60)
    )
    source += (
        "\n\n```\n" + ("X" * 300 + "\n") * 60 + "LAST_CODE_LINE\n```\n\nEND_REPORT"
    )
    doc = _read(source)
    text = "".join(page.extract_text() for page in doc.pages)
    assert len(doc.pages) >= 4
    assert "Paragraph 0" in text and "Paragraph 59" in text
    assert "LAST_CODE_LINE" in text and "END_REPORT" in text
    assert text.count("X") == 300 * 60


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", ""),
        ("language", "en_US"),
        ("source", "Bad\x01text"),
        ("source", "Unsupported 漢"),
    ],
)
def test_renderer_validation(field: str, value: str) -> None:
    arguments = {"source": "Text", "title": "Test", "language": "und"}
    arguments[field] = value
    with pytest.raises(ValueError):
        PdfRenderer().render(**arguments)


def test_code_blank_lines_and_tabs_preserve_text() -> None:
    doc = _read("Text\tspacing\n\n```\nfirst\n\n\tsecond\n```\n")
    text = "".join(page.extract_text() for page in doc.pages)
    assert "first" in text and "second" in text


def test_wide_number_marker_does_not_overlap_item_text() -> None:
    doc = _read("123456789. First\n\n           continuation\n")
    positions: dict[str, float] = {}

    def visit(
        text: str, current: list[float], matrix: list[float], font: object, size: float
    ) -> None:
        for label in ("123456789.", "First", "continuation"):
            if label in text:
                positions[label] = current[4] + matrix[4]

    doc.pages[0].extract_text(visitor_text=visit)
    assert positions["First"] > positions["123456789."] + pdfmetrics.stringWidth(
        "123456789.", "BGDXSans", 11
    )
    assert positions["continuation"] == pytest.approx(positions["First"])


def test_excessive_nesting_is_a_clean_error() -> None:
    with pytest.raises(ValueError, match="nesting"):
        _read("> " * 15 + "Text")


def test_fonts_register_without_machine_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Force registration even if prior tests have populated ReportLab's registry.
    monkeypatch.setattr(pdfmetrics, "getRegisteredFontNames", lambda: [])
    assert _read("# Font coverage").pages


def test_cli_publish_metadata_overwrite_and_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, output = tmp_path / "source.md", tmp_path / "out.pdf"
    source.write_text("# Čćšžđ Ћирилица", encoding="utf-8-sig")
    original = source.read_bytes()
    application = PublisherApplication()
    monkeypatch.setattr(
        "bgdxpublisher.cli.publish.PublisherApplication", lambda **kw: application
    )
    command = [
        "publish-pdf",
        str(source),
        "--output",
        str(output),
        "--title",
        "Izveštaj",
        "--lang",
        "sr-Cyrl",
    ]
    assert main(command) == 0
    assert application.state is RuntimeState.STOPPED
    assert source.read_bytes() == original
    document = PdfReader(output)
    assert document.metadata.title == "Izveštaj"
    assert document.trailer["/Root"]["/Lang"] == "sr-Cyrl"
    assert "Čćšžđ Ћирилица" in document.pages[0].extract_text()
    monkeypatch.undo()
    before = output.read_bytes()
    assert main(command) == 1
    assert output.read_bytes() == before
    source.write_text("# New", encoding="utf-8")
    assert main([*command, "--overwrite"]) == 0
    assert "New" in PdfReader(output).pages[0].extract_text()


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["x.md"],
        ["x.md", "--output", "x.pdf", "--lang", "en_US"],
        ["x.md", "--output", "x.pdf", "--title", ""],
        ["x.md", "--output", "x.pdf", "--theme", "dark"],
    ],
)
def test_cli_invalid_arguments(args: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        main(["publish-pdf", *args])
    assert error.value.code == 2


def test_path_failures_and_source_preservation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, output = tmp_path / "source.md", tmp_path / "out.pdf"
    source.write_text("# Original", encoding="utf-8")
    original = source.read_bytes()
    service = PdfPublishingService(logging.getLogger("test"))
    result = service.publish(PdfRequest(source, output))
    assert result.bytes_written == len(output.read_bytes())
    assert PdfReader(output).metadata.title == "source"
    assert source.read_bytes() == original
    previous = output.read_bytes()
    with pytest.raises(PublishingError, match="different files"):
        service.publish(PdfRequest(source, source, True))
    alias = tmp_path / "alias.pdf"
    alias.hardlink_to(source)
    with pytest.raises(PublishingError, match="different files"):
        service.publish(PdfRequest(source, alias, True))
    with pytest.raises(PublishingError, match="regular file"):
        service.publish(PdfRequest(tmp_path, output, True))
    with pytest.raises(PublishingError, match="extension"):
        service.publish(PdfRequest(source, tmp_path / "wrong.html"))
    with pytest.raises(PublishingError):
        service.publish(PdfRequest(tmp_path / "missing.md", output, True))
    with pytest.raises(PublishingError):
        service.publish(PdfRequest(source, tmp_path / "missing" / "out.pdf"))
    source.write_bytes(b"\xff")
    with pytest.raises(PublishingError):
        service.publish(PdfRequest(source, output, True))
    assert output.read_bytes() == previous
    source.write_text("Unsupported 漢", encoding="utf-8")
    assert (
        main(["publish-pdf", str(source), "--output", str(output), "--overwrite"]) == 1
    )
    assert output.read_bytes() == previous
    source.write_text("# Original", encoding="utf-8")

    def fail(*args: object) -> None:
        raise OSError("commit failed")

    monkeypatch.setattr(PublishingService, "write_bytes", fail)
    with pytest.raises(PublishingError, match="commit failed"):
        service.publish(PdfRequest(source, output, True))
    assert output.read_bytes() == previous
    assert source.read_bytes() == original


@pytest.mark.parametrize(
    "failure", [LayoutError("layout failed"), TTFError("font failed")]
)
def test_layout_and_font_failure_are_cli_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    source = tmp_path / "source.md"
    source.write_text("Text", encoding="utf-8")

    def fail(*args: object) -> bytes:
        raise failure

    monkeypatch.setattr(PdfRenderer, "render", fail)
    assert (
        main(["publish-pdf", str(source), "--output", str(tmp_path / "out.pdf")]) == 1
    )
