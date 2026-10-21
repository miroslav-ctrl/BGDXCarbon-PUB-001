"""Verify the installed DOCX batch CLI and retain distinct CLI visual samples."""

import logging
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile

from docx import Document

import bgdxpublisher
from bgdxpublisher.cli.docx_batch import run_docx_batch
from bgdxpublisher.docx_batch_pipeline import (
    BatchDocxPublicationService,
    BatchDocxRequest,
)
from bgdxpublisher.runtime import PublisherApplication, RuntimeFoundationError


def verify(root: Path) -> None:
    """Use a real installed executable outside checkout, then inject stop failures."""
    assert "site-packages" in Path(bgdxpublisher.__file__).parts
    root.mkdir(parents=True, exist_ok=True)
    source = root / "sources"
    source.mkdir()
    (source / "notes.MD").write_text(
        "# Beleške / Белешке\n\n> Independent quote.\n\n"
        "3. Third step\n4. Fourth step\n\n`Code sample`",
        encoding="utf-8",
    )
    (source / "report.md").write_text(
        "# Čć Ћирилица\n\n**Bold report** with *emphasis*.\n\n"
        "## Findings\n\n- First\n- Second\n\n[Reference](https://example.com)",
        encoding="utf-8-sig",
    )
    before = {p: p.read_bytes() for p in source.iterdir()}
    output = root / "published"
    config = root / "config.yaml"
    config.write_text(
        "app:\n  name: Test\n  version: 1.1.0\n"
        "logging:\n  level: CRITICAL\n  console: false\n",
        encoding="utf-8",
    )
    cli = Path(sys.executable).parent / (
        "bgdxpublisher.exe" if os.name == "nt" else "bgdxpublisher"
    )
    command = [
        str(cli),
        "publish-docx-batch",
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
            f"Published: {output / (p.stem + '.docx')}\n"
            for p in sorted(source.iterdir())
        )
        + "Batch complete: 2 published, 0 failed.\n"
    )
    assert completed.stdout == expected
    logger = logging.getLogger("installed-direct")
    logger.setLevel(logging.CRITICAL)
    direct = BatchDocxPublicationService(logger).publish(
        BatchDocxRequest(source, root / "direct", language="sr-Latn")
    )
    for item in direct.items:
        target = output / item.output.name
        doc = Document(target)
        assert doc.core_properties.title == item.source.stem
        assert doc.core_properties.language == "sr-Latn"
        with ZipFile(target) as actual, ZipFile(item.output) as expected_zip:
            assert set(actual.namelist()) == set(expected_zip.namelist())
            assert all(
                actual.read(n) == expected_zip.read(n) for n in actual.namelist()
            )
    previous = {p: p.read_bytes() for p in output.iterdir()}
    failed = run(command)
    assert (
        failed.returncode == 1
        and failed.stdout == "Batch complete: 0 published, 2 failed.\n"
    )
    assert failed.stderr == "".join(
        f"Failed: item={i} DOCX_PUBLICATION_FAILED stage=validate\n" for i in (1, 2)
    )
    assert all(p.read_bytes() == b for p, b in previous.items())
    (output / "report.docx").unlink()
    mixed = run(command)
    assert (
        mixed.returncode == 1
        and mixed.stdout == f"Published: {output / 'report.docx'}\n"
        "Batch complete: 1 published, 1 failed.\n"
    )
    assert mixed.stderr == "Failed: item=1 DOCX_PUBLICATION_FAILED stage=validate\n"
    (source / "report.md").write_bytes(b"\xff")
    bad = run([*command, "--overwrite"])
    assert (
        bad.returncode == 1
        and bad.stderr == "Failed: item=2 DOCX_PUBLICATION_FAILED stage=read\n"
    )
    (source / "report.md").write_bytes(before[source / "report.md"])
    preflight = run([*command[:2], str(root / "missing"), *command[3:]])
    assert preflight.returncode == 1 and preflight.stdout == ""
    assert preflight.stderr == "Batch publication failed: BATCH_DOCX_PREFLIGHT_FAILED\n"
    for tail in (["--lang", "en_US"], ["--index"], ["--output", "other"]):
        rejected = run([*command, *tail])
        assert rejected.returncode == 2 and rejected.stdout == ""
    assert run([str(cli), "publish-docx-batch", "--help"]).returncode == 0
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
        assert run_docx_batch(source, output, True, config, "sr-Latn") == 1
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
        patch.object(BatchDocxPublicationService, "publish", unexpected_publish),
    ):
        try:
            run_docx_batch(source, output, True, config, "sr-Latn")
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
