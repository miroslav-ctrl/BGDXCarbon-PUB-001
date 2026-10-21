"""Host/dev-only PDF semantic verification; never imported by the runtime wheel."""

import sys
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject, StreamObject


def pdf_value(value):
    """Compare dereferenced resource meaning, independent of object IDs/encoding."""
    if isinstance(value, IndirectObject):
        return pdf_value(value.get_object())
    if isinstance(value, StreamObject):
        return (
            {
                str(k): pdf_value(v)
                for k, v in value.items()
                if k not in ("/Length", "/Filter", "/DecodeParms")
            },
            value.get_data(),
        )
    if isinstance(value, DictionaryObject):
        return {str(k): pdf_value(v) for k, v in value.items()}
    if isinstance(value, ArrayObject):
        return [pdf_value(v) for v in value]
    return value


def assert_pdf_equivalent(actual_path, expected_path):
    """Match complete decoded content/resources and document/page semantics."""
    actual, expected = PdfReader(actual_path), PdfReader(expected_path)
    assert actual.trailer["/Root"]["/Lang"] == expected.trailer["/Root"]["/Lang"]
    # ReportLab uses wall-clock CreationDate/ModDate and variable trailer IDs.
    # All remaining metadata is compared; decoded page/font resources are exact.
    volatile = {"/CreationDate", "/ModDate"}
    assert {k: v for k, v in actual.metadata.items() if k not in volatile} == {
        k: v for k, v in expected.metadata.items() if k not in volatile
    }
    assert len(actual.pages) == len(expected.pages)
    for page, other in zip(actual.pages, expected.pages):
        assert list(page.mediabox) == list(other.mediabox)
        assert abs(float(page.mediabox.width) - 595.2756) < 0.01
        assert abs(float(page.mediabox.height) - 841.8898) < 0.01
        assert page.extract_text() == other.extract_text()
        assert page.get_contents().get_data() == other.get_contents().get_data()
        assert pdf_value(page["/Resources"]) == pdf_value(other["/Resources"])

        def links(p):
            return [
                (
                    list(a.get_object()["/Rect"]),
                    pdf_value(a.get_object().get("/A")),
                    a.get_object().get("/Subtype"),
                )
                for a in p.get("/Annots", [])
            ]

        assert links(page) == links(other)


def verify(root: Path) -> None:
    """Verify both actual new-API outputs and their complete single-API semantics."""
    paths = sorted((root / "published").glob("*.pdf"))
    assert [p.stem for p in paths] == ["multipage", "sample"]
    for path in paths:
        assert_pdf_equivalent(path, root / "individual" / path.name)
        document = PdfReader(path)
        assert document.metadata.title == path.stem
        assert document.trailer["/Root"]["/Lang"] == "sr-Latn"
        assert "Ћирилица" in "".join(p.extract_text() for p in document.pages)
        assert (
            (len(document.pages) > 1)
            if path.stem == "multipage"
            else (len(document.pages) == 1)
        )
        fonts = [
            font.get_object()
            for page in document.pages
            for font in page["/Resources"]["/Font"].values()
        ]
        assert any(
            font.get("/FontDescriptor") is not None
            and "/FontFile2" in font["/FontDescriptor"]
            for font in fonts
        )


if __name__ == "__main__":
    verify(Path(sys.argv[1]).resolve())
