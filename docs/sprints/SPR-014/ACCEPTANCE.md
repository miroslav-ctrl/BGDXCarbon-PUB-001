# SPR-014 Acceptance Criteria

Status: pending implementation. Record tested SHA, command, environment and result.

| ID | Criterion | Evidence |
| --- | --- | --- |
| AC-01 | Legacy nonrecursive discovery, case-insensitive .md selection and ordering | Mixed names/extensions and nested-directory tests |
| AC-02 | Independent jobs/contexts per attempted item | Captured job IDs/contexts and repeated calls |
| AC-03 | Byte-equivalent HTML for identical inputs/options | Differential legacy/new tests over metadata defaults, themes, TOC and UTF-8/BOM |
| AC-04 | Stem collisions and index.md conflict rejected before publication | Preflight tests with forbidden service call |
| AC-05 | Expected item failure does not stop remaining items | Mixed valid/invalid files; typed terminal results and no partial output |
| AC-06 | Source/overwrite/alias/symlink/race protections retained | Filesystem regressions and destination race injection |
| AC-07 | Index includes completed items only; independent index failure preserves documents | Index entries/escaping and failure/disk assertions |
| AC-08 | Postcommit cleanup failure is FAILED and excluded from index without rollback | Injected cleanup failure and retained file assertions |
| AC-09 | Safe logs and exactly one publication attempt per item | Spies and sentinel content/path/exception log tests |
| AC-10 | Runtime and installed wheel support success/partial/index failure | Fresh wheel environment outside checkout, including empty successful index |
| AC-11 | Existing CLI and direct APIs unchanged | Full regression suite |
| AC-12 | Quality and coverage pass in four environments | Windows/Linux Python 3.13/3.14; total >=99%, existing five and batch_pipeline each >=95% |

Implementation review, authorized merge and exact successful post-merge CI are required before issue #31 closure. Planning alone completes no criterion.
