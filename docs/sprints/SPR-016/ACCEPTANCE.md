# SPR-016 Acceptance Criteria

Status: implementation prepared for review; see IMPLEMENTATION-EVIDENCE.md. Final acceptance remains pending review, four-environment CI, visual verification and exact post-merge evidence.

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
