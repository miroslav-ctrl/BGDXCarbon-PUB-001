"""Verify built distribution identity/data and write exact-build SHA256SUMS.txt."""

import ast
import hashlib
import sys
import tarfile
import tomllib
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile


def verify(directory: Path) -> None:
    """Check source, wheel and sdist without importing the checkout package."""
    repository = Path(__file__).resolve().parents[1]
    archived_notes = repository / "docs/releases/1.1.0.md"
    assert hashlib.sha256(archived_notes.read_bytes()).hexdigest() == (
        "07bf7257f707d8db849ddefb0f5a10df586d4cb566308b2d10d91c29aa76067f"
    )
    version = tomllib.loads((repository / "pyproject.toml").read_text())["project"][
        "version"
    ]
    tree = ast.parse((repository / "src/bgdxpublisher/version.py").read_text())
    assert ast.literal_eval(tree.body[0].value) == version
    for name in ("configs/default.yaml", "src/bgdxpublisher/config/default.yaml"):
        lines = (repository / name).read_text().splitlines()
        assert [s.strip() for s in lines if s.startswith("  version:")] == [
            f"version: {version}"
        ]
    wheel = directory / f"bgdxpublisher-{version}-py3-none-any.whl"
    source = directory / f"bgdxpublisher-{version}.tar.gz"
    assert sorted(directory.glob("*.whl")) == [wheel]
    assert sorted(directory.glob("*.tar.gz")) == [source]
    with ZipFile(wheel) as archive:
        assert len(archive.namelist()) == len(set(archive.namelist()))
        wheel_files = {name: archive.read(name) for name in archive.namelist()}
    prefix = f"bgdxpublisher-{version}/"
    with tarfile.open(source, "r:gz") as archive:
        members = [member for member in archive.getmembers() if member.isfile()]
        assert len(members) == len({member.name for member in members})
        assert all(member.name.startswith(prefix) for member in members)
        source_files = {}
        for member in members:
            stream = archive.extractfile(member)
            assert stream is not None
            source_files[member.name[len(prefix) :]] = stream.read()
    wheel_metadata = BytesParser().parsebytes(
        wheel_files[f"bgdxpublisher-{version}.dist-info/METADATA"]
    )
    source_metadata = BytesParser().parsebytes(source_files["PKG-INFO"])
    for metadata in (wheel_metadata, source_metadata):
        assert metadata["Name"] == "bgdxpublisher"
        assert metadata["Version"] == version
        assert metadata["Requires-Python"] == ">=3.13"
    assert wheel_metadata.get_all("Requires-Dist") == source_metadata.get_all(
        "Requires-Dist"
    )
    # Every production module and bundled resource must match this source tree.
    package = repository / "src/bgdxpublisher"
    files = [
        path
        for path in package.rglob("*")
        if path.is_file() and path.suffix in (".py", ".yaml", ".ttf", ".txt", ".md")
    ]
    for path in files:
        name = path.relative_to(repository / "src").as_posix()
        assert wheel_files[name] == path.read_bytes(), name
        assert source_files[f"src/{name}"] == path.read_bytes(), name
    fonts = list((package / "publishing/fonts").glob("*.ttf"))
    assert len(fonts) == 5
    assert (package / "publishing/fonts/LICENSE.txt").stat().st_size > 0
    # Include executable examples: sdist tests/verification use these helpers.
    documented = [
        repository / name
        for name in (
            "README.md",
            "CHANGELOG.md",
            "RELEASE-NOTES.md",
            "MANIFEST.in",
            "pyproject.toml",
        )
    ]
    documented += list((repository / "configs").glob("*.yaml"))
    documented += list((repository / "examples").glob("*.py"))
    documented += list((repository / "docs/releases").rglob("*.md"))
    documented += list((repository / "tools").glob("*.py"))
    for path in documented:
        name = path.relative_to(repository).as_posix()
        assert source_files[name] == path.read_bytes(), name
    entries = sorted((wheel, source), key=lambda path: path.name)
    checksums = "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
        for path in entries
    )
    (directory / "SHA256SUMS.txt").write_text(checksums, encoding="utf-8", newline="\n")
    print(f"PASS: {version}, {len(files)} package files, 5 fonts/license, wheel/sdist")
    print(checksums, end="")


if __name__ == "__main__":
    verify(Path(sys.argv[1] if len(sys.argv) > 1 else "dist-review").resolve())
