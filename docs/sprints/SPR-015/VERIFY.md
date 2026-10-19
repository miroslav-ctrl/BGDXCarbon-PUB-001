# SPR-015 Verification Plan

Status: implemented for review. Commands below are the reproducible verification procedure; actual local results are in [implementation evidence](IMPLEMENTATION-EVIDENCE.md). Final review and exact post-merge CI remain required.

Install .[dev] with Python 3.13/3.14 and run:

~~~sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest tests/cli/test_batch.py tests/cli/test_batch_index.py tests/cli/test_batch_cli_pipeline.py
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pytest tests/domain --cov=bgdxpublisher.domain --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/jobs --cov=bgdxpublisher.jobs --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/pipeline --cov=bgdxpublisher.pipeline --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/orchestration --cov=bgdxpublisher.orchestration --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/html_pipeline --cov=bgdxpublisher.html_pipeline --cov-report=term-missing --cov-fail-under=95
python -m pytest tests/batch_pipeline --cov=bgdxpublisher.batch_pipeline --cov-report=term-missing --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
~~~

The new CLI test file is named test_batch_cli_pipeline.py to avoid collision with the existing batch service test module. examples/batch_cli_pipeline.py is copied and executed by the installed-wheel CI step outside checkout.

## Verification order

1. Test service selection and exact BatchRequest forwarding with legacy routes forbidden.
2. Assert exact stdout/stderr and exits for success, parser rejection, preflight, partial/all failure, index failure and combined publication/shutdown failure.
3. Exercise real filesystem collisions, aliases, overwrite refusal, races and postcommit cleanup. Check retained bytes, no unwanted temporary files and index membership.
4. Verify sentinel-safe diagnostics and logs; inject unexpected dependency exceptions and runtime initialize/start/stop failures.
5. Run differential tests and all existing regressions with the quality/coverage commands above.
6. Build/install wheel in a clean virtual environment; copy smoke scripts outside the checkout, unset source PYTHONPATH, and verify imports resolve to the installed package.
7. Against that wheel run CLI complete success, partial invalid UTF-8, overwrite refusal/success and reserved-index preflight. A copied Python harness may inject an index failure at WriteStage while invoking the CLI adapter; assert safe index stderr and preserved document outputs.
8. Verify all four CI combinations, then source review. After separately authorized merge, repeat evidence collection on the exact merge SHA and record closure.

No new dependencies or reduced coverage thresholds. Record actual counts, skips, package version, interpreter, OS and CI URLs; do not copy old SPR-014 counts as SPR-015 results.
