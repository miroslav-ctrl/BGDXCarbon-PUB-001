# SPR-015 Acceptance Criteria

Status: all pending. Planning is not implementation evidence.
Record tested SHA, environment, exact commands, results and links per criterion.

| ID | Criterion | Required verification |
| --- | --- | --- |
| AC-01 | Existing parser/signature/defaults retained | All batch options; missing required CLI arguments and parser-rejected option values exit 2 before runtime/service invocation. A syntactically valid but nonexistent source directory is an operational preflight failure with exit 1, covered by AC-06. |
| AC-02 | Registered pipeline selected exactly once | Capture BatchRequest and service call; forbid legacy publish_batch/PublishingService publication fallback. |
| AC-03 | Deterministic byte-compatible success | Compare with baseline/legacy documents and index for light/dark, TOC, index on/off, default/custom language, UTF-8/BOM and Unicode; preserve source bytes. |
| AC-04 | Existing success output contract retained | Exact ordered Published lines, document summary and optional Index published line; exit 0 after successful shutdown. |
| AC-05 | Partial/all-item failure projected correctly | Continue expected failures; correct document counts/ordinals/stages, exit 1, completed-only or empty index; exclude stale outputs. |
| AC-06 | Safe preflight errors, no publication attempt | Nonexistent/empty source directories, casefold collisions, reserved index and preflight output/alias/symlink errors produce BATCH_HTML_PREFLIGHT_FAILED and exit 1 before any item job, document publication attempt or document/index content write. Creating filesystem directories during preflight is not transactional and has no rollback guarantee; item-level validation failures remain under AC-05/AC-08. |
| AC-07 | Independent index failure reported | Stable index code, exit 1; completed document counts/output survive, no invented failed document or index success. |
| AC-08 | Race/overwrite/cleanup semantics retained | Refusal preserves existing bytes; explicit overwrite works; precommit failures clean temporaries; postcommit cleanup failure retains file, counts FAILED and excludes index entry. |
| AC-09 | Runtime lifecycle and error precedence correct | Initialize/start once; stop CONFIGURED/RUNNING on success/failure; shutdown failure suppresses buffered stdout, exits 1, preserves primary diagnostic/files; unexpected exceptions propagate. |
| AC-10 | Safe diagnostics and logs | Sentinel Markdown/title/path/raw-cause content absent from new publication stderr/logs; parser exit 2 and existing runtime diagnostic boundary documented separately. |
| AC-11 | Other commands/direct APIs remain compatible | Existing full suite; single HTML, DOCX/PDF, default runtime and legacy direct batch/index assertions unchanged except justified CLI-facing stderr updates. |
| AC-12 | Four-environment quality and installed wheel pass | Ruff, Black, MyPy, full suite, total >=99%, six package gates >=95%, wheel outside checkout success/partial/preflight/index-failure/overwrite scenarios. |

Acceptance requires source review, exact successful pre-merge CI and separately authorized merge followed by exact post-merge CI. Record actual review/authorization timing; do not retrospectively mark historical process complete without evidence. Case-sensitive/symlink tests must execute on Linux; document every Windows skip.
