"""Installed-wheel CLI verification, including an independent index race."""

import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import bgdxpublisher
from bgdxpublisher.cli.app import main
from bgdxpublisher.html_pipeline.service import WriteStage


def invoke(arguments: list[str]) -> tuple[int, str, str]:
    """Capture the real CLI adapter's streams and exit status."""
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        status = main(arguments)
    return status, stdout.getvalue(), stderr.getvalue()


def main_smoke() -> None:
    """Verify installed imports and committed bytes across CLI outcomes."""
    assert "site-packages" in Path(bgdxpublisher.__file__).parts
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "source"
        source.mkdir()
        (source / "a.md").write_text("# Čć Ћирилица", encoding="utf-8-sig")
        (source / "b.md").write_text("# B", encoding="utf-8")
        output = root / "output"
        command = ["publish-batch", str(source), "--output-dir", str(output), "--index"]
        status, stdout, _ = invoke(command)
        assert status == 0 and "2 published, 0 failed" in stdout
        assert "Index published:" in stdout
        before = {p.name: p.read_bytes() for p in output.iterdir()}
        status, stdout, stderr = invoke(command)
        assert status == 1 and stdout == ""
        assert "Batch publication failed: BATCH_HTML_PREFLIGHT_FAILED" in stderr
        assert before == {p.name: p.read_bytes() for p in output.iterdir()}
        assert invoke([*command, "--overwrite"])[0] == 0
        (source / "a.md").write_bytes(b"\xff")
        status, stdout, stderr = invoke([*command, "--overwrite"])
        assert status == 1 and "1 published, 1 failed" in stdout
        assert "Failed: item=1 HTML_PUBLICATION_FAILED stage=read" in stderr
        assert str(source) not in stderr and "Traceback" not in stderr
        assert "./a.html" not in (output / "index.html").read_text(encoding="utf-8")
        (source / "b.md").write_bytes(b"\xff")
        status, stdout, _ = invoke([*command, "--overwrite"])
        assert status == 1 and "0 published, 2 failed" in stdout
        assert "No documents were published successfully." in (
            output / "index.html"
        ).read_text(encoding="utf-8")
        (source / "a.md").write_text("# A", encoding="utf-8")
        (source / "b.md").write_text("# B", encoding="utf-8")
        race_output = root / "race"
        original = WriteStage.execute

        def execute(self, value, context):
            result = original(self, value, context)
            (race_output / "index.html").write_text("competitor", encoding="utf-8")
            return result

        with patch.object(WriteStage, "execute", execute):
            status, stdout, stderr = invoke(
                [
                    "publish-batch",
                    str(source),
                    "--output-dir",
                    str(race_output),
                    "--index",
                ]
            )
        assert status == 1 and "2 published, 0 failed" in stdout
        assert "Index publication failed: BATCH_INDEX_FAILED" in stderr
        assert "Index published:" not in stdout
        assert all((race_output / name).exists() for name in ("a.html", "b.html"))
        assert (race_output / "index.html").read_text() == "competitor"
        assert str(source) not in stderr and "Traceback" not in stderr
        (source / "index.md").write_text("# Reserved", encoding="utf-8")
        status, stdout, stderr = invoke(
            [
                "publish-batch",
                str(source),
                "--output-dir",
                str(root / "reserved"),
                "--index",
            ]
        )
        assert status == 1 and stdout == ""
        assert "BATCH_HTML_PREFLIGHT_FAILED" in stderr
        assert not (root / "reserved").exists()


if __name__ == "__main__":
    main_smoke()
