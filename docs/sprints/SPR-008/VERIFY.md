# SPR-008 verification

Local result: 203 tests passed on Windows / Python 3.14.8, total coverage 99.77%.
Ruff, Black, and MyPy passed. A freshly installed wheel outside the repository
passed existing commands and batch/index checks in both themes, overwrite refusal,
explicit replacement, and partial-failure index filtering.

Remote implementation verification: commit `efddaff` passed all four jobs in
[CI run 38144919931](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/38144919931),
including installed-wheel checks on Windows/Linux with Python 3.13/3.14.
Subsequent documentation commits trigger their own CI checks before merge.

Run Ruff, Black, MyPy, pytest coverage >=99%, and installed-wheel CI on Linux
and Windows, Python 3.13/3.14. Tests parse actual index links and check that decoded
targets exist; failures and atomic no-clobber behavior are covered separately.

Manual Windows acceptance (with Markdown files already in `documents`):

```powershell
bgdxpublisher publish-batch .\documents --output-dir .\published --theme dark --lang sr-Latn --toc --index --overwrite
Start-Process .\published\index.html
```

Expect the normal document counts plus `Index published: ...index.html`. Click
each link and verify it opens the matching document. Check the theme and Serbian
labels. Repeat using `--theme light --overwrite`, then refresh the browser and
check links in the light theme. The index tab title is `Documents`.

Repeat without `--overwrite`: expect exit 1 and the existing index and documents
to remain unchanged. Automated overwrite acceptance is already confirmed above;
manual visual/link acceptance remains pending until the user confirms it.
Final review and green CI for the final PR commit are required before merge.
