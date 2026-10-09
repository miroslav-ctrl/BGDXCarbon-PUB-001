# SPR-007 verification

Run Ruff, Black, MyPy, and pytest with coverage >=99%.
CI also installs a built wheel outside the checkout, publishes a two-file batch,
checks metadata/theme/TOC, refuses overwrites, and verifies explicit overwrite.

Manual Windows acceptance:

```powershell
New-Item -ItemType Directory -Force .\documents
Copy-Item .\document.md .\documents\first.md
Copy-Item .\document.md .\documents\second.md
bgdxpublisher publish-batch .\documents --output-dir .\published --theme dark --lang sr-Latn --toc
bgdxpublisher publish-batch .\documents --output-dir .\published --theme light --lang sr-Latn --toc --overwrite
```

Expect `2 published, 0 failed` for each command. Open both HTML outputs and check
content, tab titles, and contents navigation. Repeat without overwrite: expect
exit 1, two failures, and unchanged existing files. Manual inspection remains
pending until the user confirms it; remote CI results must be checked on the PR.
