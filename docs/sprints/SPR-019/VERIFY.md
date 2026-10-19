# SPR-019 Verification Plan

Status: proposed; commands/tests below are future implementation checks.

```sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest tests/cli/test_pdf_cli_pipeline.py tests/cli/test_pdf_runtime_precedence.py tests/publishing/test_pdf.py tests/pdf_pipeline/test_pdf_publication.py tests/cli/test_docx_runtime_precedence.py
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pip wheel . --no-deps --wheel-dir dist-review
```

New test paths are proposed, not present evidence. Keep all eight independent
>=95% package commands in ci.yml; total >=99%, Ubuntu/Windows Python 3.13/3.14.
No new package/gate/dependency. Explain every skip; execute filesystem cases Linux.

1. Capture service resolution and PdfRequest/single call, forbid legacy fallback;
   test both flags select PDF pipeline and never DOCX. Preserve all other routes.
2. Differential PDF/source comparison under identical dependencies: twelve or
   equivalent BOM/metadata/input combinations incl. multipage, no raw ZIP/PDF
   equality or broad normalization. Validate fonts/safety via retained regressions.
3. Capture exact stdout/stderr/exit; validate/read/render/write/cleanup injections
   plus real glyph/control/TTFError/LayoutError. Use sensitive sentinels and ensure
   safe publication line/logs. Parser invalid metadata/options before runtime.
4. Inject initialize/start/stop errors; cover expected publication + expected stop,
   success + expected stop, active unexpected primary + expected/unexpected stop,
   success + unexpected stop and handled typed failure + unexpected stop. Assert
   specified order/count/propagation; cross-check unchanged DOCX/HTML behavior.
5. Retain filesystem race/symlink/alias/overwrite/permissions/precommit tests;
   test postcommit engine cleanup leaves PDF and FAILED/no success, cleanup once.
6. Fresh wheel, actual publish-pdf executable from outside checkout, cleared source
   PYTHONPATH: exact success/metadata/Unicode; refusal bytes/overwrite; parser exit 2;
   safe missing/invalid extension validate, invalid UTF-8 read and glyph render exit 1.
   Keep copied PDF API smoke and all existing other CLI/API checks.
7. Actually inspect CLI pdf-preview generated through migrated route on tested
   SHA; preserve distinct API multipage and DOCX artifacts and review scope.
8. Formal source/AC review and exact-head CI before separately authorized merge;
   exact merge CI and accepted closure documentation before implementation issue completion.
