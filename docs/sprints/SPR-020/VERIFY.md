# SPR-020 Verification Plan

Status: proposed checks, no implementation evidence.

```sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest tests/docx_batch_pipeline/test_docx_batch_publication.py tests/docx_pipeline/test_docx_publication.py tests/publishing/test_docx.py
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pytest tests/docx_batch_pipeline --cov=bgdxpublisher.docx_batch_pipeline --cov-report=term-missing --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
```

New paths/gate are future work. Preserve all eight existing package gates/checks.
Run Ubuntu/Windows Python3.13/3.14; explain skips and execute filesystem cases Linux.

1. Test immutable request/item/result invariants and derived counts, terminal
   outcomes and mismatch/duplicate/empty rejection.
2. Spy child/mkdir to forbid work before preflight; missing/file/empty/lang/root
   symlink before resolution/dangling candidate/casefold collision/output alias/directory.
   Include output symlinks to selected input, unrelated target and dangling target;
   all must fail before mkdir/child calls, with overwrite both false and true.
   Setup mkdir failure must precede child calls; no rollback expectation.
3. Snapshot source enumeration once, add a file during first child call to ensure
   no rescan; .MD inclusion, subdirectory ignore, stable sort and index.md allowed.
4. Capture exact DocxRequest for each item, forbid legacy fallback, prove fresh IDs
   and OOXML/source fidelity against individual API under identical dependencies.
5. Mixed success/failure, all failed, existing refusal/overwrite, bad encoding/title,
   render/write injection; per-item states/stages/counts and later continuation.
6. Inject race/replace/flush and postcommit registered cleanup; earlier/current
   committed files retained appropriately, temp cleanup/once/context isolation.
   Inject unexpected child exception outside engine: propagate/no later attempts.
7. Capture logs with path/name/title/body/cause sentinels; preflight fixed code,
   safe per-item diagnostics, explicit result paths not misclassified as log leaks.
8. Fresh installed wheel/copy example outside checkout, removed source PYTHONPATH,
   installed-import assertion; success/mixed/all failure/refusal/overwrite/preflight
   and metadata/status/count checks. Existing actual command/API smoke retained.
9. Distinct batch-generated DOCX artifact with >=2 different inputs; render every
   output/page and inspect Unicode/layout. Record exact SHA/run/artifact/pages.
10. Formal review/exact-head CI before separately authorized merge; exact post-merge
    CI and accepted closure record before future implementation issue completion.
