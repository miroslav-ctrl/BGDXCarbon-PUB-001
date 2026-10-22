# Release 1.2.0 Candidate Acceptance

Status: candidate formal review/owner-authorized merge completed via PR #70.
Exact merged commit91f63e981feacd23bdff288e1064944386ebed56; CI39747742484
attempt2 SUCCESS. RC-01 through RC-09 technical gates PASS; publication execution
was separately authorized on 2026-10-22 under the
[publication request](PUBLICATION-REQUEST.md); tag/assets/download verification
remain execution gates.

| ID | Requirement | Evidence required |
| --- | --- | --- |
| RC-01 | Accepted scope complete | HTML/DOCX/PDF single/batch CLI/API matrix; completed SPR-020/021/022/023 issues and closure links. |
| RC-02 | One release identity | Package/runtime/both default configs1.2.0, default CLI/version/installed metadata assertions; custom config override regressions retained. |
| RC-03 | Current user documentation | Six publishing commands/APIs/install/options/exit codes/partial results/preflight/runtime/format limits; no stale future batch PDF claim. |
| RC-04 | Historical integrity | Published1.1 notes preserved byte-for-byte, published changelog history/tags/assets intact; fonts/licenses unchanged. |
| RC-05 | Both distributions | Build wheel and sdist, verify metadata and all module/resource/config/font/license bytes, examples/helpers/release docs, exact checksums and artifact provenance. |
| RC-06 | Fresh installed execution | Full actual CLI/API suite against BOTH separate wheel and sdist installs outside checkout, cleared source PYTHONPATH, runtime-only examples and host semantic checks. |
| RC-07 | Quality gates | Ruff/Black/MyPy/full tests,total>=99%,all ten packages>=95%,Ubuntu/Windows Python 3.13/3.14; explain skips and execute symlink-sensitive cases on hosted environments. |
| RC-08 | Compatibility/error contracts | Existing direct APIs/CLI/renderers/writers/fonts/lifecycle unchanged apart from version; safe errors, output timing, primary/stop/cleanup/no rollback regressions. |
| RC-09 | Cross-format samples | HTML/index/theme/navigation checks; DOCX OOXML/PDF semantic comparisons and all candidate acceptance preview pages actually opened with exact run/artifact/digest/page scope. |
| RC-10 | No premature publication | Target version unused at preparation, no main/merge/tag/release/upload; separate owner exact-head acceptance/merge/publication authorizations remain required. |

Candidate formal review/owner-authorized merge and exact post-merge CI: COMPLETE.
Publication authorization: GRANTED on 2026-10-22.
Final-source CI, tag/assets/download verification: execution gates; see the finalization PR.
See the publication request for chronology and exact execution evidence.
Automated Codex COMMENT is disclosed self-review, not independent human APPROVE.
