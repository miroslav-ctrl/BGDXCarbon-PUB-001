# SPR-002 Verification

Run from the repository root with Python 3.13 or newer and the development
extras installed:

```sh
ruff check .
black --check .
mypy src
pytest
pytest --cov=bgdxpublisher --cov-report=term-missing
```

Verify the installed commands:

```sh
bgdxpublisher --help
bgdxpublisher version
bgdxpublisher doctor
bgdxpublisher config validate
bgdxpublisher runtime status
```

Use `--config PATH` with `doctor`, `config validate`, and `runtime status` to
verify an alternate configuration.
