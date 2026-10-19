# SPR-016 Acceptance Criteria

Status: AC-01–AC-12 PASS on merged develop `c98be074d96d1bc95affa86718a91e58f52bb8a1`, verified 2026-10-19. Formal closure record is submitted for review; see [CLOSURE.md](CLOSURE.md).

| ID | Criterion | Required evidence |
| --- | --- | --- |
| AC-01 | New typed API and consistent immutable envelopes | Valid COMPLETED result; reject failed/mismatched envelopes; typed DOCX_PUBLICATION_FAILED with preserved cause chain and no partial output. |
| AC-02 | Independent jobs and deterministic stages | Fresh document/job/context IDs per call, exact stage order and terminal history, no cross-call state. |
| AC-03 | Validation before reading/publication | Invalid title/lang/extension, missing/directory source, same path/hardlink, output symlink/directory, missing parent and overwrite refusal; forbidden read/render/write spies. |
| AC-04 | UTF-8/BOM source and metadata fidelity | Serbian Latin/Cyrillic, empty Markdown, default stem/custom title, default/custom language; unchanged source bytes. |
| AC-05 | OOXML equivalence to legacy service | Member inventory and contents/semantic structure across headings, inline markup, lists/start/nesting, quotes/code, styles, metadata and relationships; only justified volatile fields normalized. |
| AC-06 | Safe content handling retained | Existing raw-HTML, safe/unsafe links, image-alt-only behavior, no external asset fetching, embedded images or macros; unchanged renderer. |
| AC-07 | Atomic writer/permissions protections | Refusal preserves bytes; overwrite succeeds; alias/symlink/race protections; injected precommit failure preserves previous outputs and cleans temporaries. |
| AC-08 | Failure/cleanup semantics | Inject validate/read/render/write/cleanup errors; exact stage and internal cause, FAILED/no result; postcommit cleanup retains committed file and runs once. |
| AC-09 | Safe logging for new route | Sentinel source/output paths, title, Markdown and cause messages absent; code/stage/job IDs allowed; legacy route boundary explicit. |
| AC-10 | Runtime and legacy compatibility | New service resolvable; legacy service still registered; CLI selects legacy DOCX and keeps arguments/output/exits/lifecycle; direct API and unrelated commands pass regressions. |
| AC-11 | Fresh installed-wheel and visual verification | New API example outside checkout validates imports and outcomes; existing DOCX CLI smoke and visual render artifact reviewed for preserved layout/Unicode. |
| AC-12 | Quality gates and review | Ruff/Black/MyPy, full suite, total >=99%, seven independent package gates >=95%, four OS/Python jobs; actual review/authorization and exact post-merge CI recorded. |

No standalone CLI migration acceptance is included. Parser errors remain exit 2
and legacy DOCX operational errors exit 1 through the unchanged command route.
New API failures are exceptions/results, not new CLI stderr contracts.
Record tested SHA, OS/Python/dependencies, commands, counts/skips, artifacts and URLs.

## Verified criterion mapping

Test names refer to tests/docx_pipeline/test_docx_publication.py unless noted.

| AC | Result and supporting evidence |
| --- | --- |
| 01 | PASS: test_equivalence checks immutable/mismatched envelopes; test_stage_failure_chain_and_safe_logs checks typed FAILED/result/cause chain. |
| 02 | PASS: stage/history assertions, test_new_api_never_calls_legacy_and_has_fresh_ids and cleanup/context isolation. |
| 03 | PASS: metadata/path cases with forbidden ReadStage, extension, parent, alias, symlink and overwrite checks. |
| 04–05 | PASS: eight BOM/metadata/empty-or-complex input combinations; all uncompressed OOXML members and member sets equal legacy, no XML normalization; source bytes retained. |
| 06 | PASS: unchanged renderer and existing tests/publishing/test_docx.py content/link/image regressions; new package member comparison excludes embedded media/macros. |
| 07 | PASS: race, replace and flush failure injection preserves bytes/temp cleanup; existing shared writer permission regressions retained. |
| 08 | PASS: metadata validation, encoding/stage/real render/flush and cleanup injection; exact failure stage/cause, retained committed DOCX, cleanup once. |
| 09 | PASS: captured safe logs, fixed job metadata and raw sentinel/path/content exclusion; legacy diagnostics unchanged. |
| 10 | PASS: test_runtime_and_single_operations and test_cli_keeps_legacy_route; existing full suite and wheel CLI regressions. |
| 11 | PASS: copied examples/docx_pipeline.py outside checkout in all four jobs; actual single-page visual inspection scoped precisely in CLOSURE.md. |
| 12 | PASS: exact post-merge CI 39225799217, seven gates and four jobs; pre-merge formal review and explicit owner merge authorization recorded. |

[CLOSURE.md](CLOSURE.md) records exact SHA/job IDs, per-environment counts, coverage,
visual artifact/review link and administrative sequence. The formal source review
is Codex COMMENT, not independent human APPROVE. Issue #39 remains open pending
acceptance/merge of this closure record. Historical implementation evidence remains
valid; this record supersedes its pending-review/CI disposition.
