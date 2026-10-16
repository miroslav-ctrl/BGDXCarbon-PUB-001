# SPR-003 Verification

Install `.[dev]` using Python 3.13 or newer, then run:

```sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pytest tests/domain --cov=bgdxpublisher.domain --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/jobs --cov=bgdxpublisher.jobs --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/pipeline --cov=bgdxpublisher.pipeline --cov-report=term-missing --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
```

Publisher core tests cover valid and invalid documents and metadata; job creation,
permitted and forbidden state transitions; stage ordering, type contracts,
validation and execution failures, empty pipelines, deterministic results,
exception causes, and cleanup behavior. The domain, jobs, and pipeline packages
must each meet at least 95% coverage.

Install the wheel in a fresh virtual environment. From a directory outside the
repository publish a UTF-8 Markdown sample, inspect the resulting HTML, confirm
existing output is refused, and verify explicit `--overwrite` succeeds. The CI
workflow runs this scenario as well as existing CLI smoke checks on all four
supported OS/Python combinations.

Test input/read/render/write failures, same paths and hard-link aliases, invalid
UTF-8, concurrent destination creation, raw HTML, unsafe links and image input.

UTF-8 input with or without a leading BOM must render the first Markdown heading
identically, preserve Serbian characters and leave the source bytes unchanged.
HTML output remains UTF-8 without a BOM. Manual Windows verification confirmed
the sample heading, Latin and Cyrillic text, list, bold text and inline code.


Post-merge verification completed on 2026-10-16: all three Copilot findings are resolved. See [SPR-003 and SPR-004 closure evidence](../SPR-004/CLOSURE-SPR-003-SPR-004.md).
