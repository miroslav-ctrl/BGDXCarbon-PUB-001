# SPR-005 Verification

Run Ruff, Black, MyPy and pytest with --cov-fail-under=99. Verify default/explicit
light equivalence, both palettes, unchanged body and metadata, escaped unsafe
content, overwrite refusal and invalid themes without output modification.
CI installs the wheel outside the repository on Windows/Linux and Python 3.13/3.14,
and checks both themes and invalid-choice exit code 2.

Manual visual verification remains pending. Open separate light/dark outputs and
inspect text, links, code blocks and quotes, including Serbian Unicode. The browser
policy previously blocked local-file navigation; the user performs this check.
