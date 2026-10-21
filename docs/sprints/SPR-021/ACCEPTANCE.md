# SPR-021 Acceptance Criteria

Status: implementation evidence submitted; formal acceptance/merge/closure pending.
See [executed evidence mapping](IMPLEMENTATION-EVIDENCE.md). Plan CI is not
implementation evidence.

| ID | Required behavior | Required evidence |
| --- | --- | --- |
| AC-01 | Thin new publish-docx-batch parser/dispatch | Exact options/defaults/help/required arguments, language validation and unsupported flags before runtime; one runtime/service/publish/exact request; no rescan/fallback. |
| AC-02 | Successful terminal projection | Deterministic item order, one Published line per COMPLETED, exact summary/counts, buffered stdout only after successful stop, exit0. |
| AC-03 | Mixed/all failure projection | Ordinals count all items; safe DOCX_PUBLICATION_FAILED stage lines, exact counts/summary/exit1, no Published for cleanup FAILED. |
| AC-04 | Safe preflight and diagnostic boundaries | Exact BATCH_DOCX_PREFLIGHT_FAILED line/exit1/no stdout, cause not traversed/stringified; content/path/name sentinels absent from safe diagnostics; argparse/runtime detail boundaries explicit. |
| AC-05 | Preserve API/filesystem/rendering | Direct BatchDocxPublicationService/DocxPublicationService/legacy API unchanged; actual batch selection/refusal/overwrite/aliases/dangling/collision policies; whole OOXML fidelity and source preservation. |
| AC-06 | Runtime shutdown and primary precedence | Full body/stop matrix from spec, startup state gates, stop once; expected stop suppresses all buffered stdout, preserves existing diagnostics; unexpected primary+safe note preserved, handled errors do not count as active primary; committed files retained. |
| AC-07 | Installed distribution and existing commands | Fresh wheel outside checkout/no source PYTHONPATH, actual new executable success/failure/parser/config; deterministic injected cleanup checks; all existing API/CLI smoke unchanged. |
| AC-08 | Actual CLI visual acceptance | >=2 differently formatted actual batch CLI DOCX outputs, render/inspect all pages, exact SHA/run/artifact/digest/page scope; retain API/single previews. |
| AC-09 | Quality and current documentation | Four matrix jobs, total>=99%, nine existing>=95% gates, Ruff/Black/MyPy; user docs/examples/changelog/release-guide aligned without version/dependency bump or historical release rewrite. |
| AC-10 | Formal review and final closure | Approved plan and separate implementation authorization, reviewed exact-head CI/owner acceptance, separately authorized merge/post-merge CI, accepted closure before issue completion; no main change/release. |

Record exact commits/environments/commands/dependencies/counts/skips/run/jobs and
actual manual inspection scope. No implementation issue completed by this plan.
