# Examples

`docx_pipeline.py` verifies the new registered DOCX pipeline API against an
installed wheel outside checkout. It compares OOXML members with the legacy
publisher, checks metadata/Unicode and exercises refusal, overwrite and failure
preservation. The existing `publish-docx` CLI continues using the legacy service.

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
