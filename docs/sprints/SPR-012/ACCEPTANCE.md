# SPR-012 Acceptance Criteria

Status: AC-01–AC-12 verified on merge 1d99a246; see [closure evidence](CLOSURE.md).

| ID | Criterion | Required evidence |
| --- | --- | --- |
| AC-01 | Successful lifecycle and exact PublishResult path/UTF-8 byte count | Service integration; immutable original job snapshots |
| AC-02 | Deterministic typed validate/read/render/write order | Stage contract and order tests |
| AC-03 | Byte-equivalent output to legacy HTML for title/lang/theme/TOC | Parameterized differential tests |
| AC-04 | Unchanged source; UTF-8/BOM and Serbian Latin/Cyrillic | Source byte hashes and output assertions |
| AC-05 | Validation/read/render/write failures produce FAILED and retain cause without partial result | Injected failures; stage identity and cause-chain assertions |
| AC-06 | Overwrite, alias/symlink, race and source protections retained | Filesystem regressions, simulated destination race |
| AC-07 | Temporary resources cleaned; committed output retained if later cleanup fails | Before/after commit failure injection and disk assertions |
| AC-08 | Isolated contexts/jobs and exactly one read/render/write per successful call | Spies and repeated-call/failure tests; no exactly-once claim across calls |
| AC-09 | Safe logs without content, paths or raw exception messages | Sentinel source/title/exception content and captured logs |
| AC-10 | Runtime and installed-wheel success/failure outside checkout | All four CI combinations; actual HTML file inspection |
| AC-11 | Legacy CLI/HTML/DOCX/PDF/batch unchanged | Complete regression suite |
| AC-12 | All quality and independent coverage gates pass | Windows/Linux × Python 3.13/3.14, total >=99%; domain/jobs/pipeline/orchestration/html_pipeline each >=95% |

Review, authorized merge and successful post-merge CI are required before issue #25 closure. Planning documentation alone completes no acceptance criterion.
