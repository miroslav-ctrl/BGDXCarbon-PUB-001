# SPR-006 Verification

Run Ruff, Black, MyPy and pytest with --cov-fail-under=99. Test unique target/link
matching, repeated/colliding labels, Unicode normalization, Cyrillic, all heading
levels, Setext, empty/punctuation headings, formatting, unsafe HTML, fenced code,
no-heading output, opt-in compatibility and overwrite/input preservation.

CI checks installed wheels outside the repository on Windows/Linux with Python
3.13/3.14. It renders both themes with --toc and checks repeated/Unicode targets.
Manual visual/click verification is pending: open both themes and click TOC entries,
including duplicate and Cyrillic headings, confirming they reach the correct section.

Review correction: retain the next suffix per normalized heading base. Repeated
headings no longer restart the occupied-suffix search; a deterministic 5,000-heading
regression verifies unique matching links and a linear set-lookup budget.
