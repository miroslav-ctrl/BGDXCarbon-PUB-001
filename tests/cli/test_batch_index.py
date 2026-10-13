"""Generated index behavior, escaping, and atomicity."""

import logging
import os
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.publishing import PublishingError, PublishingService
from bgdxpublisher.publishing.batch import BatchRequest, publish_batch


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.hrefs.append(dict(attrs)["href"] or "")


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_index_links_and_metadata(
    tmp_path: Path, theme: str, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "documents"
    source.mkdir()
    names = ["Ћирилица # 100% & [пример]", "b", "a"]
    for name in names:
        (source / (name + ".md")).write_text("# Test", encoding="utf-8")
    output = tmp_path / "out"
    args = [
        "publish-batch",
        str(source),
        "--output-dir",
        str(output),
        "--index",
        "--theme",
        theme,
        "--lang",
        "sr-Latn",
        "--toc",
    ]
    assert main(args) == 0
    html = (output / "index.html").read_text(encoding="utf-8")
    links = Links()
    links.feed(html)
    assert [unquote(p) for p in links.hrefs] == [
        "./a.html",
        "./b.html",
        "./Ћирилица # 100% & [пример].html",
    ]
    for href in links.hrefs:
        assert (output / unquote(href)).is_file()
    assert '<html lang="sr-Latn">' in html and f"color-scheme:{theme}" in html
    assert "&amp; [пример]" in html
    assert '<meta http-equiv="Content-Security-Policy"' in html
    assert "3 published, 0 failed" in capsys.readouterr().out
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    assert main(args) == 1
    assert {p.name: p.read_bytes() for p in output.iterdir()} == before
    assert "Output exists" in capsys.readouterr().err
    assert main([*args, "--overwrite"]) == 0
    assert "Index published:" in capsys.readouterr().out


@pytest.mark.parametrize("all_fail", [False, True])
def test_index_excludes_failed_and_stale_outputs(
    tmp_path: Path, all_fail: bool
) -> None:
    source = tmp_path / "input"
    source.mkdir()
    (source / "bad.md").write_bytes(b"\xff")
    if not all_fail:
        (source / "good.md").write_text("# Good")
    output = tmp_path / "output"
    output.mkdir()
    (output / "bad.html").write_text("stale")
    assert (
        main(
            [
                "publish-batch",
                str(source),
                "--output-dir",
                str(output),
                "--index",
                "--overwrite",
            ]
        )
        == 1
    )
    html = (output / "index.html").read_text()
    assert "bad.html" not in html
    assert ("good.html" in html) is (not all_fail)
    assert ("No documents were published successfully." in html) is all_fail
    assert (output / "bad.html").read_text() == "stale"


@pytest.mark.parametrize("name", ["index.md", "INDEX.MD"])
def test_index_reserved_name_preflight(tmp_path: Path, name: str) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / name).write_text("# Index")
    (source / "a.md").write_text("# A")
    output = tmp_path / "out"
    assert (
        main(
            [
                "publish-batch",
                str(source),
                "--output-dir",
                str(output),
                "--index",
                "--overwrite",
            ]
        )
        == 1
    )
    assert not output.exists()
    assert main(["publish-batch", str(source), "--output-dir", str(output)]) == 0


@pytest.mark.parametrize("alias", ["input", "output", "directory"])
def test_index_output_guard(tmp_path: Path, alias: str) -> None:
    source = tmp_path / "source"
    source.mkdir()
    document = source / "a.md"
    document.write_text("# Keep")
    output = tmp_path / "out"
    output.mkdir()
    index = output / "index.html"
    if alias == "directory":
        index.mkdir()
    else:
        target = document if alias == "input" else output / "a.html"
        if alias == "output":
            target.write_text("old")
        os.link(target, index)
    assert (
        main(
            [
                "publish-batch",
                str(source),
                "--output-dir",
                str(output),
                "--index",
                "--overwrite",
            ]
        )
        == 1
    )
    assert document.read_text() == "# Keep"
    if alias != "directory":
        assert index.read_text() == ("# Keep" if alias == "input" else "old")


def test_index_commit_failure_reports_document_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "a.md").write_text("# A")
    original = PublishingService._write

    def broken(output: Path, html: str, overwrite: bool) -> None:
        if output.name == "index.html":
            raise OSError("disk error")
        original(output, html, overwrite)

    monkeypatch.setattr(PublishingService, "_write", staticmethod(broken))
    assert (
        main(
            [
                "publish-batch",
                str(tmp_path),
                "--output-dir",
                str(tmp_path / "out"),
                "--index",
            ]
        )
        == 1
    )
    captured = capsys.readouterr()
    assert "1 published, 0 failed" in captured.out
    assert "Index publication failed:" in captured.err and "disk error" in captured.err
    assert (tmp_path / "out" / "a.html").exists()
    assert not (tmp_path / "out" / "index.html").exists()


def test_index_race_refuses_new_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "a.md").write_text("# A")
    original = PublishingService._write

    def racing(output: Path, html: str, overwrite: bool) -> None:
        if output.name == "index.html":
            output.write_text("concurrent")
        original(output, html, overwrite)

    monkeypatch.setattr(PublishingService, "_write", staticmethod(racing))
    result = publish_batch(
        PublishingService(logging.getLogger("test-index")),
        BatchRequest(tmp_path, tmp_path / "out", index=True),
    )
    assert result.index is None and result.index_error is not None
    assert (tmp_path / "out" / "index.html").read_text() == "concurrent"
    assert not list((tmp_path / "out").glob(".bgdx-*.tmp"))


def test_index_escapes_html_and_prefixes_links(tmp_path: Path) -> None:
    service = PublishingService(logging.getLogger("index-escape"))
    service.publish_index(
        tmp_path / "index.html",
        [("<script>*x*</script>", "evil:foo#%.html")],
        "und",
        "light",
        False,
    )
    html = (tmp_path / "index.html").read_text()
    assert "&lt;script&gt;*x*&lt;/script&gt;" in html
    assert "<script>" not in html
    assert 'href="./evil%3Afoo%23%25.html"' in html
    with pytest.raises(PublishingError, match="Language"):
        service.publish_index(tmp_path / "other.html", [], "en_US", "light", False)


def test_index_rechecks_output_after_document_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "a.md"
    source.write_text("# A")
    service = PublishingService(logging.getLogger("index-recheck"))
    original = service.publish

    def publish(request):
        result = original(request)
        (tmp_path / "out" / "index.html").mkdir()
        return result

    monkeypatch.setattr(service, "publish", publish)
    result = publish_batch(
        service, BatchRequest(tmp_path, tmp_path / "out", index=True)
    )
    assert result.index_error == "Output must be a regular file."
