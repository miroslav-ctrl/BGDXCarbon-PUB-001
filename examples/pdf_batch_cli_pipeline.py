"""Verify the installed PDF batch CLI and retain distinct CLI visual samples."""

import logging
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import bgdxpublisher
from bgdxpublisher.cli.pdf_batch import run_pdf_batch
from bgdxpublisher.pdf_batch_pipeline import (
    BatchPdfPublicationService,
    BatchPdfRequest,
)
from bgdxpublisher.runtime import PublisherApplication, RuntimeFoundationError


def verify(root: Path) -> None:
    """Use a real installed executable outside checkout, then inject stop failures."""
    assert "site-packages" in Path(bgdxpublisher.__file__).parts
    root.mkdir(parents=True, exist_ok=True)
    source = root / "sources"
    source.mkdir()
    (source / "sample.md").write_text(
        "# Izveštaj / Ћирилица\n\nČćžšđ **bold** *italic* `code`.\n\n"
        "- First\n  - Nested\n\n3. Third\n4. Fourth\n\n> Quote\n\n"
        "[safe](https://example.com) ![alt](https://example.com/image)\n\n"
        "```python\nprint('Здраво')\n```",
        encoding="utf-8-sig",
    )
    (source / "multipage.MD").write_text(
        "# Multipage / Ћирилица\n\n"
        + "Paragraph Čć text.\n\n" * 65
        + "## Steps\n\n3. Third\n4. Fourth\n\n"
        + "```python\n"
        + "print('Здраво')\n" * 25
        + "```",
        encoding="utf-8",
    )
    before = {p: p.read_bytes() for p in source.iterdir()}
    output = root / "published"
    config = root / "config.yaml"
    config.write_text(
        "app:\n  name: Test\n  version: 1.2.0\n"
        "logging:\n  level: CRITICAL\n  console: false\n",
        encoding="utf-8",
    )
    cli = Path(sys.executable).parent / (
        "bgdxpublisher.exe" if os.name == "nt" else "bgdxpublisher"
    )
    command = [
        str(cli),
        "publish-pdf-batch",
        str(source),
        "--output-dir",
        str(output),
        "--config",
        str(config),
        "--lang",
        "sr-Latn",
    ]
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}

    def run(args):
        return subprocess.run(args, cwd=root, env=env, capture_output=True, text=True)

    completed = run(command)
    assert completed.returncode == 0 and completed.stderr == ""
    expected = (
        "".join(
            f"Published: {output / (p.stem + '.pdf')}\n"
            for p in sorted(source.iterdir())
        )
        + "Batch complete: 2 published, 0 failed.\n"
    )
    assert completed.stdout == expected
    logger = logging.getLogger("installed-direct")
    logger.setLevel(logging.CRITICAL)
    direct = BatchPdfPublicationService(logger).publish(
        BatchPdfRequest(source, root / "individual", language="sr-Latn")
    )
    assert direct.success_count == 2 and direct.failure_count == 0
    assert all(item.output.read_bytes().startswith(b"%PDF-") for item in direct.items)
    previous = {p: p.read_bytes() for p in output.iterdir()}
    failed = run(command)
    assert (
        failed.returncode == 1
        and failed.stdout == "Batch complete: 0 published, 2 failed.\n"
    )
    assert failed.stderr == "".join(
        f"Failed: item={i} PDF_PUBLICATION_FAILED stage=validate\n" for i in (1, 2)
    )
    assert all(p.read_bytes() == b for p, b in previous.items())
    (output / "sample.pdf").unlink()
    mixed = run(command)
    assert (
        mixed.returncode == 1
        and mixed.stdout == f"Published: {output / 'sample.pdf'}\n"
        "Batch complete: 1 published, 1 failed.\n"
    )
    assert mixed.stderr == "Failed: item=1 PDF_PUBLICATION_FAILED stage=validate\n"
    (source / "sample.md").write_bytes(b"\xff")
    bad = run([*command, "--overwrite"])
    assert (
        bad.returncode == 1
        and bad.stderr == "Failed: item=2 PDF_PUBLICATION_FAILED stage=read\n"
    )
    (source / "sample.md").write_bytes(before[source / "sample.md"])
    preflight = run([*command[:2], str(root / "missing"), *command[3:]])
    assert preflight.returncode == 1 and preflight.stdout == ""
    assert preflight.stderr == "Batch publication failed: BATCH_PDF_PREFLIGHT_FAILED\n"
    for tail in (["--lang", "en_US"], ["--index"], ["--output", "other"]):
        rejected = run([*command, *tail])
        assert rejected.returncode == 2 and rejected.stdout == ""
    assert run([str(cli), "publish-pdf-batch", "--help"]).returncode == 0
    (source / "multipage.MD").write_text("Unsupported 漢 SECRET", encoding="utf-8")
    glyph = run([*command, "--overwrite"])
    assert glyph.returncode == 1
    assert (
        glyph.stdout == f"Published: {output / 'sample.pdf'}\n"
        "Batch complete: 1 published, 1 failed.\n"
    )
    assert glyph.stderr == "Failed: item=1 PDF_PUBLICATION_FAILED stage=render\n"
    assert "SECRET" not in glyph.stderr and "6F22" not in glyph.stderr
    (source / "multipage.MD").write_bytes(before[source / "multipage.MD"])
    overwritten = run([*command, "--overwrite"])
    assert overwritten.returncode == 0 and overwritten.stdout == completed.stdout
    assert all(p.read_bytes() == b for p, b in before.items())
    assert not list(output.glob(".bgdx-*.tmp"))
    # Installed adapter failure injection, no production testing hooks.
    original_stop = PublisherApplication.stop

    def stop(app):
        original_stop(app)
        raise RuntimeFoundationError("installed-stop")

    from contextlib import redirect_stderr, redirect_stdout
    from io import StringIO

    stdout, stderr = StringIO(), StringIO()
    with (
        patch.object(PublisherApplication, "stop", stop),
        redirect_stdout(stdout),
        redirect_stderr(stderr),
    ):
        assert run_pdf_batch(source, output, True, config, "sr-Latn") == 1
    assert (
        stdout.getvalue() == ""
        and stderr.getvalue() == "Runtime cleanup failed: installed-stop\n"
    )
    assert all(p.exists() for p in previous)
    primary = ValueError("installed-primary")

    def unexpected_stop(app):
        original_stop(app)
        raise RuntimeError("SECRET-installed-stop")

    def unexpected_publish(*args):
        raise primary

    with (
        patch.object(PublisherApplication, "stop", unexpected_stop),
        patch.object(BatchPdfPublicationService, "publish", unexpected_publish),
    ):
        try:
            run_pdf_batch(source, output, True, config, "sr-Latn")
        except ValueError as error:
            assert error is primary
            assert error.__notes__ == [
                "An unexpected runtime cleanup failure occurred."
            ]
        else:
            raise AssertionError("unexpected primary swallowed")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        verify(Path(sys.argv[1]).resolve())
    else:
        with TemporaryDirectory() as directory:
            verify(Path(directory))
