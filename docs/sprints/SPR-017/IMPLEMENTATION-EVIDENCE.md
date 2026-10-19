# SPR-017 Implementation Evidence

Status: implemented for review, 2026-10-19. Issue #43 open; no merge or closure.
Baseline: develop 9e7cb64a97a1dff545c498afafa5f8527fb9a202, approved plan PR #42.

## Implementation boundaries

Only cli/publish.py changes production behavior: DOCX branch selects registered
DocxPublicationService and adapts result.publication; typed DOCX failure joins the
existing safe code/stage diagnostic path. PDF-first dispatch stays intact.
Unexpected DOCX primary failure survives unexpected shutdown with a safe note;
handling is scoped to docx and not pdf. Other unexpected shutdown paths retain
their existing propagation behavior. Expected runtime failures retain existing
cleanup-before-primary ordering and suppress success output without rollback.

Parser, both direct DOCX APIs, renderer/writer, engines, registration, dependencies
and version are unchanged. The prior SPR-016 CLI-legacy spy is replaced by a
direct legacy API regression; new CLI spies enforce pipeline selection. Historical
SPR-016 evidence remains unchanged rather than rewritten to imply CLI migration then.

## Acceptance mapping

New CLI cases: tests/cli/test_docx_cli_pipeline.py (15 cases) and
tests/cli/test_docx_runtime_precedence.py (7 cases).

| AC | Evidence prepared for review |
| --- | --- |
| 01 | Existing DOCX argument tests; test_parser_failure_never_initializes_runtime |
| 02 | Eight test_docx_routing_and_equivalence cases capture exact request and forbid fallback; test_pdf_first_when_both_flags |
| 03–04 | Exact Published stdout, eight UTF-8/BOM × metadata × input combinations compare all uncompressed OOXML members/member sets and source bytes; no XML normalization |
| 05–06 | Injected stage errors with safe sentinel/path exclusion, missing-source validation and parser exit 2; real installed CLI read/validate errors |
| 07 | Existing pipeline filesystem/overwrite/race/permissions regressions; installed CLI refusal preserves existing bytes and explicit overwrite succeeds |
| 08 | test_postcommit_cleanup_failure_retains_output; inherited pipeline cleanup once/context tests; FAILED stage=cleanup with retained DOCX and no Published stdout |
| 09 | Expected shutdown after success/primary failure, init/start lifecycle, four unexpected shutdown/primary × DOCX/HTML combinations; no masked primary or changed HTML behavior |
| 10 | test_legacy_direct_api_retains_contract plus existing new API and full suite; PDF-first spy, unchanged HTML/PDF/batch tests |
| 11 | Expanded actual executable checks in installed-wheel CI step; retained API smoke and visual sample generation; fresh local CLI execution below, actual CI image review pending |
| 12 | Local results below; four-environment CI/seven package gates and source review remain required |

## Completed local checks

Windows / Python 3.13.14: full suite **465 passed, 4 skipped**; total coverage
**99.85%** (2058 statements, 3 missed), cli/publish.py **100%** (47 statements).
Targeted DOCX CLI/runtime/pipeline/legacy tests: **70 passed, 1 skipped**.
Full-suite skips: batch case-sensitive collision, batch directory symlink,
HTML output symlink and DOCX output symlink privileges. Linux CI must execute them.

Ruff passes; Black checks 98 Python files; MyPy checks 59 source files without
issues. git diff --check passes. Tests executed outside sandbox in the isolated
development environment. Initial missing local basetemp parent was corrected;
figures above are successful completed runs, not failed setup attempts.

Wheel 1.1.0 SHA-256:
28060b67585db8a83922f84948e03e5f93902f1cb81ce42dd249c8cc71778a76.
Built and installed in a fresh venv; real bgdxpublisher.exe executed from outside
checkout with PYTHONPATH empty. Parent verification used isolated Python (-I).
Success confirms Unicode/editable DOCX and metadata/exact stdout; refusal preserves
bytes; overwrite succeeds; invalid metadata exits 2; missing/invalid UTF-8 source
exits 1 with safe validate/read diagnostics and no traceback/path leakage. Previous
output bytes remain intact. Workflow exercises corresponding actual CLI checks
alongside all retained API/other-command/visual checks in four environments.

Final CI, actual visual artifact review, source review, separately authorized merge
and exact post-merge acceptance/closure remain required before closing #43.
