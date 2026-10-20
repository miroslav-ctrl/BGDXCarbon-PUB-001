# SPR-020 Acceptance Criteria

Status: all pending. Baseline/plan CI is not implementation acceptance.

| ID | Criterion | Required evidence |
| --- | --- | --- |
| AC-01 | Typed immutable aggregate | Request/defaults, terminal item invariants, completed matching output/failed no output; frozen tuple, reject empty/duplicate/nonterminal/mismatched results; derived counts. |
| AC-02 | Read-only preflight | Invalid lang/root/empty/collision/output-directory/source symlink/dangling/output alias cases; no mkdir/child calls before checks. |
| AC-03 | Deterministic snapshot | Nonrecursive case-insensitive .md only; sorted stable names, index.md allowed, source snapshot captured once; no rescan during child calls. |
| AC-04 | Single pipeline reuse | Registered single service exactly once per selected source/exact request, no legacy fallback; fresh jobs/context across items/repeated calls. |
| AC-05 | DOCX fidelity | UTF-8/BOM/Unicode/empty/different inputs; all uncompressed OOXML members/metadata/lang/styles/lists/links vs individual API; source unchanged. |
| AC-06 | Partial/all failures | Typed child errors continue; ordered terminal items/counts for mixed/all failed; refused bytes retained and eligible later items run. |
| AC-07 | Filesystem protection | Directory setup errors safe preflight/no children; every output symlink (including dangling/unrelated target), selected-input aliases and destination directories rejected before mkdir/children; atomic race/permissions/precommit/temp policy retained. |
| AC-08 | Cleanup/unexpected failure | Postcommit cleanup failed item/file retained/continue, cleanup once; unexpected external child error propagates/stops later attempts, earlier commits remain; no rollback. |
| AC-09 | Safe diagnostics boundary | Fixed BATCH_DOCX_PREFLIGHT_FAILED/cause; safe item stage/code; no raw paths/names/title/body/bytes/cause in logs/string; explicit paths allowed in API results. |
| AC-10 | Runtime/API/CLI compatibility | New service composes registered DOCX service, caller owns lifecycle; all current commands/direct APIs/engine/renderer/writer unchanged and regressions pass. |
| AC-11 | Installed wheel/visuals | Fresh installed API outside checkout success/mixed/all failure/refusal/overwrite/preflight/status/metadata; actual >=2 batch DOCX outputs/all pages inspected, existing previews retained. |
| AC-12 | Quality/review/closure | Four matrix jobs, total >=99%, nine independent >=95% gates (old eight intact), Ruff/Black/MyPy; formal review/owner authorization/exact merge CI and accepted closure before issue completion. |

Record exact SHA/environments/dependencies/commands/counts/skips, run/job/artifact
links and actual page inspection scope. No new CLI behavior is accepted here.
