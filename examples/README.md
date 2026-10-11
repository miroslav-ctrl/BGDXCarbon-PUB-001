# Examples

From the repository root, publish a single document:

```powershell
bgdxpublisher publish .\examples\documents\report.md --output .\report.html --title "Izveštaj" --lang sr-Latn --theme dark --toc
```

Publish both sample documents with an index:

```powershell
bgdxpublisher publish-batch .\examples\documents --output-dir .\example-output --lang sr-Latn --theme light --toc --index
Start-Process .\example-output\index.html
```

Use `--overwrite` on subsequent runs to replace generated files explicitly.
Expected batch count is `2 published, 0 failed`, plus the separate index report.
