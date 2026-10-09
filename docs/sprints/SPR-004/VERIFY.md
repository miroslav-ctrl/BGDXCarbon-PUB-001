# SPR-004 Verification

Run Ruff, Black, MyPy and pytest with `--cov-fail-under=99`. Verify default metadata,
Unicode and escaped titles, language/script/region examples, invalid metadata,
unchanged Markdown body and preservation of input and existing output on errors.

The four Windows/Linux, Python 3.13/3.14 CI jobs also install a wheel outside the
repository and check custom metadata, overwrite and invalid language rejection.
Manual browser check: use `--title "Izveštaj" --lang sr-Latn`, inspect the browser
 tab title and HTML `lang` attribute. Visual manual verification is pending.
