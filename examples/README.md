# Examples

`docx_pipeline.py` verifies the new registered DOCX pipeline API against an
installed wheel outside checkout. It compares OOXML members with the legacy
publisher, checks metadata/Unicode and exercises refusal, overwrite and failure
preservation. The existing `publish-docx` CLI uses the registered DOCX pipeline;
the direct legacy service remains available with its original API contract.

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

`pdf_pipeline.py` verifies the registered PDF pipeline API from an installed wheel
outside checkout: completion/fresh jobs, refusal/overwrite and safe encoding
failure with retained output. Run `python -I pdf_pipeline.py [output-directory]`;
an optional directory retains sample.pdf and multipage.pdf for host pypdf and
visual checks. Its verification uses runtime dependencies only. Existing
publish-pdf CLI uses the registered PDF pipeline; direct legacy PdfPublishingService
retains its original contract.

`docx_batch_pipeline.py` verifies the registered batch DOCX API; the development
command `publish-docx-batch` reuses it without changing direct API contracts.
`docx_batch_cli_pipeline.py` verifies the actual installed executable outside
checkout: config/metadata/Unicode/OOXML fidelity, refusal/overwrite/mixed/all
failure/preflight/parser diagnostics and injected runtime-stop behavior. Run
`python -I docx_batch_cli_pipeline.py [output-directory]` from an installed wheel;
optional directory retains two distinct CLI-generated DOCX visual samples.
These development additions target accepted release1.2.0; no publication implied.

`pdf_batch_pipeline.py` verifies the registered batch PDF API from an installed
wheel outside checkout using runtime dependencies only. Run `python -I
pdf_batch_pipeline.py [output-directory]`; optional output retains one single-page
and one multipage batch-generated PDF plus individual API equivalents.
`pdf_batch_verify.py OUTPUT` is a host/dev-only pypdf semantic verifier for those
outputs, including complete decoded content/resources, metadata/lang/links/fonts.
It is not a runtime dependency or CLI command. Existing PDF/DOCX/HTML examples
remain. Batch PDF CLI is reserved for SPR-023; release1.2.0 is not yet published.

`pdf_batch_cli_pipeline.py` verifies the actual installed publish-pdf-batch command
outside checkout (success/mixed/all/refusal/overwrite/read/glyph/preflight/parser,
configuration and injected runtime-stop failures). Run `python -I
pdf_batch_cli_pipeline.py OUTPUT` from an installed wheel. It retains sample.pdf
and multipage.pdf from the CLI plus direct batch API equivalents in individual/.
Run `python pdf_batch_verify.py OUTPUT` in the host/dev environment for full PDF
semantic comparison; pypdf is not a runtime dependency. Distinct CLI preview
artifacts render every acceptance sample page for inspection. No release is made.
