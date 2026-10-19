# SPR-018 Verification Plan

Status: proposed; no new commands/tests executed as implementation evidence.

Future implementation checks after separate authorization:

```sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest tests/pdf_pipeline/test_pdf_publication.py tests/publishing/test_pdf.py
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pytest tests/pdf_pipeline --cov=bgdxpublisher.pdf_pipeline --cov-report=term-missing --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
```

Preserve all seven existing package gates in ci.yml; add PDF as eighth.
Execute Ubuntu/Windows Python 3.13/3.14. Explain every skip and execute filesystem
cases on Linux. Retain all existing CLI, API, wheel and visual checks.

1. Validate immutable result/error invariants, job history, stage order/types,
   one read/render/write and fresh IDs/contexts across repeated calls.
2. Differential pypdf comparison with legacy, UTF-8/BOM × metadata × inputs,
   source bytes, safe links/fonts and multipage structure; preserve safety tests.
3. Forbid read/render/write on invalid validation inputs; inject read/encoding,
   unsupported glyph, font/LayoutError, render/write and cleanup failures.
   Assert stage/FAILED/internal cause; capture logs with sensitive sentinels.
4. Inject no-overwrite race, write/flush/replace precommit failures and postcommit
   cleanup; assert previous bytes/temp cleanup or committed file retention as
   appropriate. No rollback claim. Verify cleanup once/context isolation.
5. Spy CLI service selection to prove legacy PDF retained and both-flags PDF-first;
   keep parser/exit/error/stdout and runtime lifecycle tests unchanged.
6. Fresh installed wheel: copy examples/pdf_pipeline.py outside checkout,
   clear source PYTHONPATH, verify imports come from installation and exercise
   success, metadata/Unicode, overwrite refusal/replacement and safe error. Retain
   actual publish-pdf and other-command executable checks.
7. Generate distinct new-API PDF preview from shipped sample and multipage/code
   fixture; render to pages, open every page, record run/artifact/SHA/pages and
   actual findings. Existing legacy CLI preview alone cannot prove new API route.
8. Formal source/AC review and exact-head CI before separately authorized merge;
   exact post-merge CI and accepted closure record before completing future issue.
