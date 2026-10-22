# SPR-023 Implementation Evidence

Submitted 2026-10-22; not final closure. Plan PR #66 merged at
`66c1a3b80f7650343633b05ef1425fcc61aded19`; exact plan post-merge CI39740035241
tracked separately. Owner explicitly authorized planning, implementation and merge.
Tracking [issue #67](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/67)
remains open until final accepted closure. No release1.2.0 publication here.

## Local checks

Windows Python3.13.14: full697passed/65filesystem skips,total99.72%,2459statements/
7missing; new adapter43statements100%. New67cases:52passed/15skips
(14symlink privilege cases/1case-sensitive collision). Existing50filesystem skips
retain baseline behavior; Linux CI must execute these cases. Ruff passes,
Black121files unchanged, MyPy67source files passes.

Commands: python -m pytest tests/cli/test_pdf_batch_cli_pipeline.py
 tests/cli/test_pdf_batch_runtime_precedence.py -q; full pytest
--cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99;
ruff check ., black --check --workers1 ., mypy src; pip wheel . --no-deps
--wheel-dir dist-review. Initial no-build-isolation attempt lacked setuptools in
shared test environment; standard isolated wheel build succeeds. No production
change was needed for that environment issue.

Local wheel1.1.0 SHA256
`b7ababfa4c1adf826476bba2370dcb13bd771d871ca831cb04b3abddeb1d564d`.
Fresh installed-wheel full CI block and actual CLI/host semantic checks are
recorded in PR when complete; do not equate build alone with installed proof.
Exact implementation head/merge runs/jobs/counts/skips and actual ALL-page visual
inspection provenance are recorded in PR once available.

## Acceptance mapping

- AC-01: new cli/pdf_batch.py and app.py new import/subparser only; exact
  registered BatchPdfPublicationService request once. Source/output Path,
  defaults/lang/config/help/parser rejection and no abbreviations tested.
- AC-02/03: success/mixed/all ordered projection with derived summary, ordinal
  counts include completed predecessors. Expected failure continuation; cleanup
  FAILED item is never Published. stdout buffered until successful stop.
- AC-04/05: safe exact BATCH_PDF_PREFLIGHT_FAILED/no synthetic counts, safe
  per-item PDF_PUBLICATION_FAILED stage reports; real INFO sentinel checks.
  API-only preflight policies retained: root/candidate/output symlinks/dangling/
  dirs/aliases/collisions/refusal/overwrite. Real render/glyph/read/write/cleanup
  cases and source/refused-byte retention. Direct batch API semantic equivalence
  uses existing host/dev helper, including metadata/A4/pages/text/decoded streams/
  all resources/font data/lang/links with only established volatile date/ID and
  stream transport normalization. Existing APIs/renderer/fonts/writer untouched.
- AC-06: all18body/stop combinations, startup-state boundaries, constructor
  propagation, close-once/config routing/stream timing, primary identity and fixed
  safe unexpected-stop note. Real unexpected child preserves earlier commit and
  stops later items; no rollback.
- AC-07: examples/pdf_batch_cli_pipeline.py uses installed actual command and
  runtime-only imports; existing examples/pdf_batch_verify.py runs in host/dev.
  Installed success/mixed/all/refusal/overwrite/read/glyph/preflight/parser/config
  and injected expected/unexpected shutdown cases; existing smoke blocks retained.
- AC-08: distinct pdf-batch-cli-preview from actual new command, one sample and
  one multipage PDF; rasterize and inspect every page before accepting. Existing
  API/single/DOCX previews preserved. Upload is not manual visual proof.
- AC-09: full/static checks/ten independent gates/total>=99% and four-env CI,
  user docs/examples/changelog/release guide aligned to development CLI.
  No version/dependency/history changes; package remains1.1.0 until release prep.
- AC-10: plan/implementation reviews and exact merge CI recorded separately.
  Owner authorization is in this task. Final closure review/acceptance/evidence
  must precede issue completion. Main/release/tag unchanged.
