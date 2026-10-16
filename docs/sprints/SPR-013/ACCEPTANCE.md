# SPR-013 Acceptance Criteria

Status: AC-01–AC-10 verified on merge 8bff0cf3; see [closure evidence](CLOSURE.md).

| ID | Criterion | Evidence |
| --- | --- | --- |
| AC-01 | HTML dispatch resolves HtmlPublicationService only | Service-selection spy and forbidden legacy call |
| AC-02 | Arguments/defaults and HTML bytes remain compatible | Metadata/theme/TOC/config and UTF-8/BOM differential tests |
| AC-03 | Success returns 0 and one Published: <path> line | Captured stdout and file bytes |
| AC-04 | Parser failure returns 2 before publication; operational failure returns 1 | Invalid arguments/metadata and missing source/write failure |
| AC-05 | Safe primary diagnostic contains stable code and stage | Sentinel exception/content tests; no traceback or raw cause text |
| AC-06 | Runtime closes; simultaneous shutdown failure preserves primary error | Lifecycle spies and cleanup failure tests |
| AC-07 | Filesystem protections and no-rollback boundary preserved | Source/output bytes, overwrite/race regressions and postcommit failure |
| AC-08 | DOCX/PDF/batch/direct legacy API behavior retained | Complete command/API regression suite |
| AC-09 | Installed wheel CLI works outside checkout | Real success/failure on all four environments |
| AC-10 | All quality and coverage gates pass | Windows/Linux × Python 3.13/3.14; total >=99%; five package gates >=95% |

Review and exact successful post-merge CI are required before closing #28. Planning alone completes no criterion.
