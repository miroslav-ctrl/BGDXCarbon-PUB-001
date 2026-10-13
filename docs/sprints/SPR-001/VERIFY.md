# SPR-001 Verification

Use Python 3.13 or newer. Install the project and its quality tools with:

```shell
python -m pip install -e ".[dev]"
```

Run the required quality gates from the repository root:

```shell
ruff check .
black --check .
mypy src
pytest
pytest --cov=bgdxpublisher --cov-report=term-missing
```

Runtime subsystem coverage must be at least 95%.
