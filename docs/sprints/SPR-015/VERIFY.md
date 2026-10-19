# SPR-015 Verification Plan

Status: planned commands and scenarios, not executed results.

Install .[dev] with Python 3.13/3.14 and run:

~~~sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest tests/cli/test_batch.py tests/cli/test_batch_index.py tests/cli/test_batch_pipeline.py
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

tests/cli/test_batch_pipeline.py is a proposed future file, absent at planning baseline. Do not report the targeted command as currently passing.

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
