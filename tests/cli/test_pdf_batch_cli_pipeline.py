"""New PDF batch command contracts and compatibility with direct APIs."""

import logging
from dataclasses import replace
from pathlib import Path
from runpy import run_path

import pytest

from bgdxpublisher.cli.app import main
from bgdxpublisher.pdf_batch_pipeline import (
    BatchPdfPublicationService,
    BatchPdfRequest,
)
from bgdxpublisher.pdf_pipeline.service import RenderStage, WriteStage
from bgdxpublisher.publishing.pdf import PdfPublishingService


def inputs(tmp_path):
    source = tmp_path / "secret-source"
    source.mkdir()
    (source / "A.md").write_text("", encoding="utf-8")
    (source / "b.MD").write_text(
        "# Čć Ћирилица\n\n**Bold** *italic*\n\n- One\n- Two\n\n[link](https://example.com)",
        encoding="utf-8-sig",
    )
    (source / "index.md").write_text(
        "# Index allowed\n\n> Quote\n\n3. Three", encoding="utf-8"
    )
    (source / "nested").mkdir()
    (source / "nested" / "skip.md").write_text("skip")
    config = tmp_path / "config.yaml"
    config.write_text(
        "app:\n  name: Test\n  version: 1.1.0\n"
        "logging:\n  level: CRITICAL\n  console: false\n",
        encoding="utf-8",
    )
    output = tmp_path / "out"
    return (
        source,
        output,
        [
            "publish-pdf-batch",
            str(source),
            "--output-dir",
            str(output),
            "--config",
            str(config),
        ],
    )


@pytest.mark.parametrize("language", ["und", "sr-Latn"])
def test_routing_fidelity_and_overwrite(tmp_path, monkeypatch, capsys, language):
    source, output, args = inputs(tmp_path)
    request = BatchPdfRequest(source, tmp_path / "direct", language=language)
    direct = BatchPdfPublicationService(logging.getLogger("direct")).publish(request)
    before = {p: p.read_bytes() for p in source.iterdir() if p.is_file()}
    calls = []
    original = BatchPdfPublicationService.publish

    def publish(self, value):
        calls.append(value)
        return original(self, value)

    monkeypatch.setattr(BatchPdfPublicationService, "publish", publish)
    monkeypatch.setattr(
        PdfPublishingService, "publish", lambda *a: pytest.fail("legacy fallback")
    )
    if language != "und":
        args += ["--lang", language]
    assert main(args) == 0
    assert calls == [replace(request, output_dir=output)]
    captured = capsys.readouterr()
    assert (
        captured.out
        == "".join(f"Published: {output / p.output.name}\n" for p in direct.items)
        + "Batch complete: 3 published, 0 failed.\n"
    )
    assert captured.err == ""
    compare = run_path(str(Path(__file__).parents[2] / "examples/pdf_batch_verify.py"))[
        "assert_pdf_equivalent"
    ]
    for item in direct.items:
        compare(output / item.output.name, item.output)
    previous = {p: p.read_bytes() for p in output.iterdir()}
    assert main(args) == 1
    captured = capsys.readouterr()
    assert captured.out == "Batch complete: 0 published, 3 failed.\n"
    assert captured.err == "".join(
        f"Failed: item={i} PDF_PUBLICATION_FAILED stage=validate\n" for i in (1, 2, 3)
    )
    assert all(p.read_bytes() == b for p, b in previous.items())
    assert main([*args, "--overwrite"]) == 0
    capsys.readouterr()
    assert calls[-1] == replace(request, output_dir=output, overwrite=True)
    assert all(p.read_bytes() == b for p, b in before.items())


@pytest.mark.parametrize(
    "tail",
    [
        [],
        ["source"],
        ["source", "--output", "out"],
        ["source", "--output-dir", "out", "--title", "x"],
        ["source", "--output-dir", "out", "--index"],
        ["source", "--output-dir", "out", "--theme", "dark"],
        ["source", "--output-dir", "out", "--toc"],
        ["source", "--output-dir", "out", "--recursive"],
        ["source", "--output-dir", "out", "--lang", "en_US"],
        ["source", "--output-dir", "out", "--overw"],
        ["source", "--output-dir", "out", "--output", "other"],
    ],
)
def test_parser_rejection_before_runtime(monkeypatch, capsys, tail):
    monkeypatch.setattr(
        "bgdxpublisher.cli.pdf_batch.PublisherApplication",
        lambda **k: pytest.fail("runtime on parser failure"),
    )
    with pytest.raises(SystemExit) as error:
        main(["publish-pdf-batch", *tail])
    assert error.value.code == 2
    assert capsys.readouterr().out == ""


def test_help_and_defaults(monkeypatch, capsys):
    from bgdxpublisher.cli.app import build_parser

    monkeypatch.setattr(
        "bgdxpublisher.cli.pdf_batch.PublisherApplication",
        lambda **k: pytest.fail("runtime on help"),
    )
    with pytest.raises(SystemExit) as error:
        main(["publish-pdf-batch", "--help"])
    assert error.value.code == 0
    assert "publish-pdf-batch" in capsys.readouterr().out
    parsed = build_parser().parse_args(
        ["publish-pdf-batch", "source", "--output-dir", "out"]
    )
    assert parsed.source == Path("source") and parsed.output_dir == Path("out")
    assert (parsed.overwrite, parsed.config, parsed.lang) == (False, None, "und")


@pytest.mark.parametrize(
    "mode", ["missing", "empty", "file", "directory", "collision", "alias"]
)
def test_real_preflight(tmp_path, capsys, mode):
    source, output, args = inputs(tmp_path)
    if mode == "missing":
        args[1] = str(source / "missing")
    elif mode == "empty":
        args[1] = str(source / "nested")
        (source / "nested" / "skip.md").unlink()
    elif mode == "file":
        args[1] = str(source / "A.md")
    elif mode == "directory":
        output.mkdir()
        (output / "A.pdf").mkdir()
    elif mode == "collision":
        (source / "a.MD").write_text("collision")
        if len([p for p in source.iterdir() if p.stem.casefold() == "a"]) != 2:
            pytest.skip("case-insensitive filesystem")
    elif mode == "alias":
        import os

        output.mkdir()
        os.link(source / "b.MD", output / "A.pdf")
    assert main(args) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Batch publication failed: BATCH_PDF_PREFLIGHT_FAILED\n"


@pytest.mark.parametrize(
    "mode", ["read", "validate", "render", "glyph", "write", "cleanup"]
)
def test_real_partial_failures(tmp_path, monkeypatch, capsys, caplog, mode):
    source, output, args = inputs(tmp_path)
    before = (source / "A.md").read_bytes()
    if mode == "read":
        (source / "b.MD").write_bytes(b"\xff")
    elif mode == "glyph":
        (source / "b.MD").write_text("Unsupported 漢 SECRET-BODY", encoding="utf-8")
    elif mode == "validate":
        output.mkdir()
        (output / "b.pdf").write_bytes(b"previous")
    else:
        stage = RenderStage if mode == "render" else WriteStage
        original = stage.execute

        def execute(self, value, context):
            if value.options.source.name == "b.MD":

                def fail():
                    raise RuntimeError("SECRET-cause " + str(source))

                if mode == "cleanup":
                    context.register_cleanup(fail)
                else:
                    fail()
            return original(self, value, context)

        monkeypatch.setattr(stage, "execute", execute)
    assert main(args) == 1
    captured = capsys.readouterr()
    assert (
        captured.out == f"Published: {output / 'A.pdf'}\n"
        f"Published: {output / 'index.pdf'}\n"
        "Batch complete: 2 published, 1 failed.\n"
    )
    stage_name = "render" if mode == "glyph" else mode
    assert captured.err == f"Failed: item=2 PDF_PUBLICATION_FAILED stage={stage_name}\n"
    assert (
        "SECRET" not in captured.err + caplog.text
        and str(source) not in captured.err + caplog.text
    )
    assert (source / "A.md").read_bytes() == before
    if mode == "validate":
        assert (output / "b.pdf").read_bytes() == b"previous"
    else:
        assert (output / "b.pdf").exists() == (mode == "cleanup")
    assert not list(output.glob(".bgdx-*.tmp"))


@pytest.mark.parametrize("overwrite", [False, True])
@pytest.mark.parametrize(
    "mode",
    [
        "root",
        "candidate",
        "dangling",
        "output-dir",
        "output-input",
        "output-unrelated",
        "output-dangling",
    ],
)
def test_symlink_preflight(tmp_path, capsys, mode, overwrite):
    source, output, args = inputs(tmp_path)
    target = source
    link = tmp_path / "link"
    if mode in ("candidate", "dangling"):
        link = source / "link.md"
        target = source / ("A.md" if mode == "candidate" else "missing")
    elif mode == "output-dir":
        target = source
        args[3] = str(link)
    elif mode.startswith("output-"):
        output.mkdir()
        link = output / "A.pdf"
        target = source / "A.md"
        if mode == "output-unrelated":
            target = tmp_path / "other"
            target.write_text("keep")
        elif mode == "output-dangling":
            target = tmp_path / "missing"
    try:
        link.symlink_to(target, target_is_directory=mode in ("root", "output-dir"))
    except OSError:
        pytest.skip("symlink privilege unavailable")
    if mode == "root":
        args[1] = str(link)
    if overwrite:
        args.append("--overwrite")
    assert main(args) == 1
    captured = capsys.readouterr()
    assert (
        captured.out == ""
        and captured.err == "Batch publication failed: BATCH_PDF_PREFLIGHT_FAILED\n"
    )


def test_operational_logs_omit_input_and_cause(tmp_path, capsys):
    source, output, args = inputs(tmp_path)
    config = Path(args[-1])
    config.write_text(
        "app:\n  name: Test\n  version: 1.1.0\n"
        "logging:\n  level: INFO\n  console: true\n",
        encoding="utf-8",
    )
    (source / "b.MD").write_bytes(b"\xffSECRET-BODY")
    assert main(args) == 1
    captured = capsys.readouterr()
    assert "Failed: item=2 PDF_PUBLICATION_FAILED stage=read\n" in captured.err
    assert "Pipeline failed" in captured.err
    for secret in (
        str(source),
        str(output),
        "secret-source",
        "b.MD",
        "SECRET-BODY",
        "UnicodeDecodeError",
        "Traceback",
    ):
        assert secret not in captured.err
