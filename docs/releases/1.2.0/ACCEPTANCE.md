# Release 1.2.0 Final Acceptance

Status: publication acceptance COMPLETE; RC-01 through RC-10 PASS.
Recorded 2026-10-23 on the basis of the published tag/release, successful exact-source
CI and actual downloaded wheel/sdist verification. See [closure evidence](CLOSURE.md)
for exact source/run/job/asset identities, hashes, execution scope and limits.

| ID | Requirement | Satisfied requirement / retained evidence | Result |
| --- | --- | --- | --- |
| RC-01 | Accepted scope complete | HTML/DOCX/PDF single/batch CLI/API matrix; completed SPR-020/021/022/023 issues and closure links. | PASS |
| RC-02 | One release identity | Package/runtime/both default configs 1.2.0, default CLI/version/installed metadata assertions; custom config override regressions retained. | PASS |
| RC-03 | Current user documentation | Six publishing commands/APIs/install/options/exit codes/partial results/preflight/runtime/format limits; no stale future batch PDF claim. | PASS |
| RC-04 | Historical integrity | Published 1.1 notes preserved byte-for-byte, published changelog history/tags/assets intact; fonts/licenses unchanged. | PASS |
| RC-05 | Both distributions | Build wheel and sdist, verify metadata and all module/resource/config/font/license bytes, examples/helpers/release docs, exact checksums and artifact provenance. | PASS |
| RC-06 | Fresh installed execution | Full actual CLI/API suite against BOTH separate wheel and sdist installs outside checkout, cleared source PYTHONPATH, runtime-only examples and host semantic checks. | PASS |
| RC-07 | Quality gates | Ruff/Black/MyPy/full tests,total >=99%,all ten packages >=95%,Ubuntu/Windows Python 3.13/3.14; explain skips and execute symlink-sensitive cases on hosted environments. | PASS |
| RC-08 | Compatibility/error contracts | Existing direct APIs/CLI/renderers/writers/fonts/lifecycle unchanged apart from version; safe errors, output timing, primary/stop/cleanup/no rollback regressions. | PASS |
| RC-09 | Cross-format samples | HTML/index/theme/navigation checks; DOCX OOXML/PDF semantic comparisons and all candidate acceptance preview pages actually opened with exact run/artifact/digest/page scope. | PASS |
| RC-10 | No premature publication | No premature publication: separate owner candidate/request acceptance, merge and publication authorizations obtained; final date/status and successful exact-source CI preceded tagging. main unchanged. All gates PASS; see CLOSURE.md. | PASS |

All matrix requirements above are satisfied by the closure record and its linked
CI/execution evidence. RC-09 manual inspection is limited to the 20 recorded pages.
Release acceptance is complete; this documentation PR integration requires its own
CI/review/merge record. Automated COMMENT is disclosed self-review, not independent
human APPROVE.
