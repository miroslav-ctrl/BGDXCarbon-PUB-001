# SPR-022 Verification Plan

Status: proposed checks only; no implementation evidence. Current baseline
CI39579108707 confirms existing develop, not future batch PDF behavior.

Proposed after separate implementation authorization:

```sh
python -m ruff check .
python -m black --check .
python -m mypy src
python -m pytest tests/pdf_batch_pipeline/test_pdf_batch_publication.py tests/pdf_pipeline/test_pdf_publication.py tests/publishing/test_pdf.py
python -m pytest
python -m pytest --cov=bgdxpublisher --cov-report=term-missing --cov-fail-under=99
python -m pytest tests/pdf_batch_pipeline --cov=bgdxpublisher.pdf_batch_pipeline --cov-report=term-missing --cov-fail-under=95
python -m pip wheel . --no-deps --wheel-dir dist-review
```

New paths/gate are future work. Retain/run ALL nine existing independent gates;
new tenth shown above supplements rather than replaces them.

1. Immutable defaults/frozen request/item/result/tuple, terminal consistency,
   completed-output/failed-no-output, empty/duplicate guards and derived counts.
2. Spy mkdir/single publish to forbid early work on invalid language/root/source
   symlink BEFORE resolve/missing/file/empty/collision/output-root policy. Cover
   immediate .MD, nested ignore/index.md, stable sort; add input during first child
   publish and prove frozen snapshot/no rescan.
3. Both overwrite modes: every planned output symlink to input/unrelated/dangling,
   output directories and hardlinks to another selected source rejected before
   mkdir/children. Directory setup expected failure safe/no child/no rollback.
   Allow same input/output root with safe distinct mapped paths.
4. Inject registered PdfPublicationService identity, spy exact PdfRequest/once,
   forbid legacy fallback, observe fresh jobs/documents/context across items/calls.
5. Compare PDFs with identical single API requests/dependencies via host pypdf:
   page count/order/A4, extracted text/Unicode, decoded content streams, font/
   resource/encoding/embedded-font semantics, title/lang/URI annotations and source
   bytes. UTF-8/BOM/empty/rich formatting/single/multipage. Document each observed
   ID/timestamp/serialization exclusion narrowly; retain real content assertions.
6. Real refusal/overwrite/mixed/all failures/bad encoding/title/unsupported glyph
   and control cases, injected font/TTFError/LayoutError/render/write; correct
   ordered statuses/stages/counts, later eligible outputs, refused bytes retained.
7. Atomic link race/replace/fsync/permission/temp unlink injections; precommit
   source/previous bytes preserved/no temporary leftovers when cleanup succeeds.
   Registered postcommit cleanup once/isolated context/file retained/failed count/
   later continuation. Writer cleanup remains write stage. Unexpected external
   child error propagates, stops later calls, earlier outputs retained.
8. Capture actual logs/string with source/name/title/Markdown/bytes/cause/glyph
   sentinels; fixed preflight code and internal __cause__, safe structured metadata.
   Explicit result paths are API data, not logging leaks; do not broaden claims
   to legacy diagnostics or propagated unexpected exceptions.
9. Fresh venv wheel outside checkout/clear PYTHONPATH/copied example -I/installed
   import assertion. New API runtime-only example: success/mixed/all failure/
   refusal/overwrite/preflight/glyph/encoding/status/counts; host pypdf checks
   returned artifacts outside venv. Keep actual installed existing CLI/API tests.
10. New API creates >=2 distinct success PDFs including single/multipage. Rasterize
    ALL pages and actually inspect every page, record SHA/run/job/artifact/digest/
    page names. Retain previous DOCX/PDF/API/CLI previews and scope claims precisely.
11. Full/static/four-env CI,total>=99%,all ten gates>=95%, docs/examples/development
    release-guide accurate/no version/dependency bump/history rewrite. Check old
    commands/direct APIs/renderer/fonts/writer/engine/lifecycle unchanged.
12. Formal plan/implementation reviews, owner acceptances/separate authorizations,
    exact post-merge CI and accepted closure before future issue completion.

Planning inspection: existing pdf_pipeline/service.py, docx_batch_pipeline,
runtime registration, installed pdf_pipeline example, SPR-020/021 specs/closure,
accepted release scope and current CI. Planning diff/link/UTF-8/AC checks and CI
are recorded separately from future implementation acceptance.
