# SPR-002 Verification

Use Python 3.13 or newer from the repository root:

```shell
ruff check .
black --check .
mypy src
pytest
pytest --cov=bgdxpublisher --cov-report=term-missing
```

Install the package before checking the generated console entry point:

```shell
python -m pip install -e .
bgdxpublisher --help
bgdxpublisher version
bgdxpublisher doctor
bgdxpublisher config validate
bgdxpublisher runtime status
```

Commands that load configuration can be directed to a temporary or custom
configuration file with `--config PATH`. Expected exit codes are 0 for
successful validation/status, and 1 for a validation failure or mandatory
doctor/runtime failure. Doctor warnings alone return 0.
