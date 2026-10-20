# SPR-020 Verification Plan

Status: implementation verification in progress; see evidence below.

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

New paths/gate implemented. Preserve all eight existing package gates/checks.
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

## Implementation evidence (2026-10-20)

Baseline develop: 5a1e2816f3d01fdbeb22c24298db2f1a81ac3f21, approved plan #54.
Implementation issue #55; branch feature/spr-020-docx-batch.

- Local Windows Python 3.13.14 / pytest 9.1.1: full coverage suite 566 passed,
  20 skipped, 2261 statements/5 missing, 99.78% (required >=99%).
- New dedicated package: 20 passed/15 skipped, 97.87% (required >=95%).
  Fourteen symlink variants and one case collision skip locally; existing suite
  adds four symlink skips and one case collision. Linux CI must execute these.
- Ruff passes; Black 108 files unchanged; MyPy 63 source files passes.
- Wheel built: bgdxpublisher-1.1.0-py3-none-any.whl, SHA256
  d705c1600292959f61a034890ad5845395b544aa6b1bcaba4f9bbda41261034b.
- Full workflow installed-wheel Python block executed locally: fresh temporary
  venv, dependencies installed, outside checkout and cleared PYTHONPATH, isolated
  new example; existing orchestration/HTML/batch/DOCX/PDF API and actual CLI retained.
  Final result and exact-head CI/visual artifact scope recorded in PR evidence.

AC mapping: AC-01 request/defaults/frozen tuple/duplicates/item envelope tests;
AC-02/03/07 preflight parametrization, symlink/alias/hardlink/mkdir guards and
snapshot added-file test; AC-04 runtime registered-single identity/exact requests/
fresh IDs; AC-05 all uncompressed OOXML members (no XML exclusions)/Unicode/BOM/
empty/index/different documents/source preservation; AC-06 refusal/mixed/all-failed/
overwrite; AC-08 typed render/write/cleanup continuation, once/context isolation,
external unexpected propagation, atomic link race/replace/fsync/permission/temp
unlink boundaries; AC-09 safe preflight cause and log sentinel checks; AC-10 full
regression suite with unchanged commands/direct publishers/engine/writer/renderer;
AC-11 fresh-wheel example plus distinct batch preview; AC-12 nine gates/total CI,
formal acceptance and separately authorized merge/closure remain pending.

Production changes are confined to new docx_batch_pipeline and runtime constructor
registration. Each batch service reuses the registered single DOCX publisher;
caller retains lifecycle ownership. Existing eight gates and previews are retained.
No new dependency/version, command, rollback or main change.
