# BGDXCarbon HTML Publisher 1.0.0

First stable release of the Markdown-to-HTML command-line publisher.

- Single-document and non-recursive batch publication.
- Standalone UTF-8 HTML with embedded light/dark themes.
- Browser title and document language options.
- Optional table of contents with unique Unicode heading targets.
- Optional batch index with encoded relative links to successful publications.
- Atomic output commits and explicit overwrite protection.
- Runtime configuration, logging, diagnostics, and per-file batch reports.

Python 3.13+ is required. Windows/Linux and Python 3.13/3.14 are tested in CI.
Install the attached wheel using `python -m pip install PATH_TO_WHEEL`.
The source distribution and SHA256SUMS.txt accompany the wheel.

The package and defaults move from 0.1.0 to 1.0.0. Existing commands remain
available. No HTML format or visual changes are introduced by release preparation.
User acceptance already confirmed themes, contents navigation, batch publication,
index appearance and link navigation. Automated checks cover overwrite refusal,
explicit replacement, Unicode, safe rendering, partial errors and atomic commits.

Limits: HTML CLI only; no PDF/DOCX export, custom templates, embedded external
images, recursive batch scan, hosting, or graphical UI. New publication without
overwrite requires filesystem hard-link support. Batch publication is atomic per
file and retains successes when another document fails. Language validation uses
a subset of BCP 47 rather than registry-based validation.
