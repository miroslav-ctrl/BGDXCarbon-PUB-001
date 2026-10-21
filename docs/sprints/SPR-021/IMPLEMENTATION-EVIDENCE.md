# SPR-021 Implementation Evidence

Submitted 2026-10-21 for Draft review, not final acceptance or closure.
Baseline develop c65c64c337c0ca9d2ad147e17456b2ef3e3852e4 (approved plan#58;
post-merge CI39572990286). Branch feature/spr-021-docx-batch-cli;
[implementation issue#59](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/59)
remains open until formal review/owner acceptance/separately authorized merge/
exact post-merge CI/accepted closure.

## Executed local checks

Windows Python3.13.14, pytest9.1.1/pytest-cov7.1.0/coverage7.16.2:
full suite617passed/35filesystem skips,2312statements/5missing,total99.78%.
New66cases:51pass/15skips (14symlink privilege cases +1case-sensitive collision).
Existing20filesystem skips belong to baseline. Hosted CI must execute Linux cases.
New cli/docx_batch.py43statements100%; cli/app.py108statements100% in full suite.
Ruff passes; Black112files unchanged; MyPy64source files passes.

Commands: ruff check ., black --check ., mypy src; focused two new CLI test files;
pytest --cov=bgdxpublisher --cov-report=term --cov-fail-under=99; pip wheel .
--no-deps --wheel-dir dist-review. All nine existing package gates remain unchanged
in ci.yml. No runtime/development dependency or version changes.

Local wheel bgdxpublisher-1.1.0-py3-none-any.whl SHA256
`e9c1daf37a7c0835e641f710824ae4e9cc9bad5f9b46235fa4c7421d70557689`.
Full CI installed-wheel Python block executed separately with fresh temporary
venv/outside checkout/cleared PYTHONPATH, copied new CLI example -I and existing
actual CLI/API examples: PASS, exit0. Exact-head CI/manual visual scope
are recorded in PR evidence; this file does not substitute baseline CI as new
implementation proof or assert uninspected artifact pages were reviewed.

## AC mapping and boundaries

- AC-01: new app.py subparser only, allow_abbrev=False scoped to it, exact options/
  defaults/config/lang/dispatch, parser exit2/help0 before runtime. New adapter
  resolves registered batch service once and publishes exact BatchDocxRequest once.
  Existing parser entries/handlers/signatures remain unchanged.
- AC-02/03: exact stdout/stderr tests for all success/refusal/overwrite/mixed/all
  failure, ordinal2 after completed predecessor, exact summary/derived counts;
  no Published for FAILED registered cleanup. Buffer stdout until successful stop.
- AC-04: real missing/empty/file/collision/alias/directory/symlink/dangling cases,
  safe preflight string and no stdout; actual INFO logs checked for filename/path/
  content/exception leakage in read failure. Expected publication diagnostics safe;
  argparse/runtime/config detail explicitly outside that guarantee.
- AC-05: full OOXML inventory/all uncompressed members vs direct batch API under
  same dependencies, no XML exclusions; Unicode/BOM/empty/index/different sources,
  refused/source bytes preserved. Batch API/single/legacy/renderer/writer/engine
  and runtime implementation unchanged; existing regressions retained.
- AC-06: eighteen body/stop combinations assert exact streams/order/counts,
  primary identity, one fixed safe note/no stop cause; six startup state/error
  cases, constructor propagation and actual unexpected child stopping after
  earlier commit. Expected stop suppresses all buffered stdout/no rollback;
  handled preflight/error/result is not an active unexpected primary. Installed
  example injects real stop failure/file retention and unexpected primary+stop.
- AC-07: examples/docx_batch_cli_pipeline.py uses real installed executable and
  --config, success/refusal/overwrite/mixed/read/all/preflight/parser/help,
  metadata/OOXML/source bytes; keeps every previous wheel smoke block.
- AC-08: new docx-batch-cli-preview generation through actual new executable,
  two distinct DOCX inputs, PDF/PNG all-page rendering; existing batch API and
  single DOCX/PDF previews retained. Actual inspection evidence in PR when ready.
- AC-09: full/static suite and four-job CI with total>=99%/nine>=95% gates.
  README/USER-GUIDE/examples/CHANGELOG current development descriptions and release
  guide updated to nine gates; published1.1.0 notes remain untouched.1.2.0 not shipped.
- AC-10: final formal implementation review/owner acceptance/authorized merge/
  exact post-merge CI/accepted closure pending; no issue completion in this PR.

Production changes confined to new cli/docx_batch.py and app.py new import/subparser.
No change to existing CLI adapters/direct APIs or any core/renderer/writer/runtime
service; no release/tag/main modification or branch deletion.
