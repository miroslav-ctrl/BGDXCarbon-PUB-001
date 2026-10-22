# Release 1.2.0 Candidate Verification

Run from candidate checkout with supported Python; retain exact command outputs.

```sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pip install build
python -m build --outdir dist-review
python tools/verify_distributions.py dist-review
```

Retain all ten independent package>=95% gates in .github/workflows/ci.yml.
That workflow's installed verification block loops through wheel and source
archive, creates a separate fresh venv for each, installs the distribution and
runs all actual retained CLI/API checks outside checkout with PYTHONPATH cleared.
Copied new API/CLI examples run under -I; pypdf semantic verification is host/dev
only. Validate version/config/metadata/help and successful/mixed/all/refused/
overwrite/preflight/glyph/read/cleanup/startup/primary precedence behaviors.

Inspect SHA256SUMS.txt against both downloaded archives; verify package data
including default config and five bundled fonts/license against checkout. Do not
compare timestamps/whole archive hashes across independent builds. Inspect the
archived published 1.1.0 notes digest and unchanged historical changelog section.

CI uploads candidate-distributions-${os}-py${python} for all four environments.
Record the exact head/run/jobs/artifact IDs/digests and installed results in PR.
Open every page in all seven retained visual acceptance artifacts, recording
actual page names/counts and limiting manual claims to inspected samples. Keep
DOCX OOXML and PDF semantic assertions; do not replace them with PNG appearance
or byte equality that ignores documented PDF volatility.

Before merge/publication recheck develop/main, target tag/release availability,
final diff and owner acceptance. This preparation executes no merge/tag/release.
