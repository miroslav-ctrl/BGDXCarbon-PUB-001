# BGDXCarbon Publisher Suite 1.2.0 candidate

Publish UTF-8 Markdown as standalone HTML, editable DOCX, or selectable-text PDF.
All three formats support single and batch CLI/API publication. HTML includes
an optional index, embedded light/dark styling and heading navigation. All
formats support document title/language metadata. Windows and Linux with Python 3.13/3.14
are covered by CI.

## Install

This branch is an unpublished 1.2.0 candidate; published v1.1.0 remains available
from [GitHub Releases](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/releases).
Python 3.13 or newer is required. Obtain the candidate wheel and SHA256SUMS.txt
from this candidate PR's CI artifacts; verify its checksum before installing.
In PowerShell, from the directory containing the downloaded wheel and checksums.
Compare the displayed hash with its SHA256SUMS entry before the install command:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Get-Content .\SHA256SUMS.txt
Get-FileHash .\bgdxpublisher-1.2.0-py3-none-any.whl -Algorithm SHA256
python -m pip install .\bgdxpublisher-1.2.0-py3-none-any.whl
bgdxpublisher version
bgdxpublisher doctor
```

Linux uses `source .venv/bin/activate` after creating the environment. An editable
checkout can be installed with `python -m pip install -e ".[dev]"`.

## Publish one document

```powershell
bgdxpublisher publish .\document.md --output .\document.html --title "Izveštaj" --lang sr-Latn --theme dark --toc
```

The output parent directory must exist. Existing output requires `--overwrite`.
`--title` changes the browser tab title; headings come from the Markdown source.
Defaults are filename stem as title, `und` (unspecified language), light theme,
and no table of contents. Supported theme values are `light` and `dark`.

## Publish a directory and index

```powershell
bgdxpublisher publish-batch .\documents --output-dir .\published --theme light --lang sr-Latn --toc --index
Start-Process .\published\index.html
```

Only immediate regular `.md` files are selected, case-insensitively; subdirectories
are ignored. Output directories are created. Each document uses its filename
stem as title. `--index` adds `index.html`, with links only to successfully
published documents from this invocation. The index title is `Documents`.
With `--index`, `index.md` is reserved and case-insensitive duplicate output names
are rejected. Without `--index`, a source named `index.md` is allowed.

Each output commits atomically. Expected individual failures do not stop other
documents. Successful outputs remain on a partial failure; the command is not
a batch transaction. Index errors are reported separately from document counts.
Repeating a batch against existing output requires `--overwrite`.

## Publish DOCX

Publish an editable Word document:

```powershell
bgdxpublisher publish-docx .\document.md --output .\document.docx --title "Izveštaj" --lang sr-Latn
```

DOCX supports CommonMark headings, paragraphs, emphasis, lists, quotations, code,
and HTTP/HTTPS/mailto hyperlinks. Images become plain alternative text; relative
and fragment links remain visible labels. Raw HTML remains visible text.
The title is metadata, while visible headings come from Markdown. Output uses
A4 portrait pages with 2.5 cm margins. Existing output requires `--overwrite`;
the parent directory must exist. HTML commands are unchanged.
The 1.2.0 candidate includes `publish-docx-batch` and its registered Python API;
custom templates remain future work. DOCX is included in version 1.1.0; the older v1.0.0 package supports HTML only.

## Publish PDF

Publish PDF directly without Word, LibreOffice,
browser installation or operating-system fonts:

```powershell
bgdxpublisher publish-pdf .\document.md --output .\document.pdf --title "Izveštaj" --lang sr-Latn
```

CommonMark text, headings, emphasis, lists, quotes, code and safe HTTP(S)/mailto
links become selectable PDF text on A4 pages with automatic pagination. Licensed
DejaVu fonts are included in the package and embedded in output, with Latin and
Cyrillic support. Unsupported glyphs fail with a safe render-stage CLI diagnostic instead
of silent replacement; legacy direct API errors retain Unicode code-point detail. Images become alternative text; raw HTML is literal
text, and relative/fragment links remain plain labels. Existing output requires
`--overwrite`, and the parent directory must exist. The title is metadata only.
HTML and DOCX commands retain their existing behavior. The 1.2.0 candidate
includes a batch PDF Python API and the publish-pdf-batch command.
Custom templates, embedded images, contents navigation and PDF/UA tagging remain
outside this foundation scope. PDF is included in version 1.1.0; the older v1.0.0 package supports HTML only.

## Publisher core API

`bgdxpublisher.domain` provides immutable document descriptors and structured
validation. `bgdxpublisher.jobs` provides immutable jobs and controlled lifecycle
transitions. `bgdxpublisher.pipeline` executes explicitly typed stages in order,
reports failures with their causes, and runs registered cleanup in reverse order.
The core is an in-process API. Registered HTML, batch HTML, DOCX, batch DOCX, PDF and batch PDF pipelines
serve the single and batch commands for all three formats.
Direct legacy services remain available with their
original contracts; publish-pdf operational failures use safe code/stage diagnostics.
See examples/pdf_pipeline.py for installed API verification.

## Commands and diagnostics

- `publish` / `publish-batch`: single/batch HTML.
- `publish-docx` / `publish-docx-batch`: single/batch DOCX.
- `publish-pdf` / `publish-pdf-batch`: single/batch PDF. Use `--help` for arguments.
- `version`: application version, Python version, environment.
- `doctor`: configuration, logging, runtime, and workspace diagnostics.
- `config validate`: validate configuration; `runtime status`: initialize and inspect runtime.
- `--config PATH` is available on publishing, doctor, config validate, and runtime status.

Exit status: 0 means success, 1 means runtime/publication failure, 2 means invalid
CLI arguments. Logs go to stderr by default; success reports go to stdout.
No-argument invocation retains runtime startup diagnostics.

## Scope and output policy

Version 1.2.0 candidate completes single/batch CLI/API coverage for HTML, DOCX and
PDF; published 1.1.0 added single DOCX/PDF, and 1.0 was HTML-only.
Custom templates, remote hosting and a graphical interface remain future work.
Raw HTML is escaped; unsafe
link schemes are refused; images render as alternative text. External images
are not embedded. Outputs use no scripts or external stylesheets.

Inputs accept UTF-8 with or without BOM. Language tags support a documented
subset: language, optional Script/REGION and non-duplicate variants; private-use
and extension forms are not supported. Existing output permissions are preserved
on POSIX overwrite; new POSIX outputs use 0644. Filesystems must support hard
links for atomic no-overwrite publication. Output symlinks are refused.

See [the usage guide](docs/USER-GUIDE.md), [examples](examples/README.md),
[release notes](RELEASE-NOTES.md), and [release process](docs/RELEASING.md).

## Batch DOCX (1.2.0 candidate)

```powershell
bgdxpublisher publish-docx-batch .\documents --output-dir .\word-output --lang sr-Latn
```

Selects immediate .md files in stable order and creates the output directory.
Use --overwrite explicitly to replace files; --config PATH selects configuration.
No title/theme/TOC/index options. Expected item failures continue and report safe
ordinal/stage diagnostics; summary counts only completed/failed documents.
Exit0 means all documents and runtime shutdown succeeded; operational/partial
failure exit1; parser error exit2. Runtime shutdown failure suppresses buffered
Published/summary lines while retaining committed files; there is no rollback.
See the usage guide for source/output symlink and alias policy. Existing commands
and direct APIs retain their contracts. This does not publish release 1.2.0.

## Batch PDF API (1.2.0 candidate)

Resolve `BatchPdfPublicationService` from an initialized/started runtime, then call
`publish(BatchPdfRequest(source_dir, output_dir, overwrite=False, language="und"))`.
Caller owns finally-stop. See examples/pdf_batch_pipeline.py for a complete
installed API example. The candidate command publish-pdf-batch reuses this API.

The API freezes immediate .md inputs in stable order, validates all source/output
symlinks/aliases/collisions before mkdir/child publication, and reuses the registered
single PDF pipeline. Expected item failures continue, including unsupported glyphs;
results expose ordered immutable terminal executions and derived counts. Safe
preflight error is BATCH_PDF_PREFLIGHT_FAILED; per-item structured stage details
remain available. Each output is independently atomic; failed cleanup can retain
committed files and there is no batch rollback. Existing direct APIs/CLI unchanged.

## Batch PDF CLI (1.2.0 candidate)

```powershell
bgdxpublisher publish-pdf-batch .\documents --output-dir .\pdf-output --lang sr-Latn
```

Uses the existing registered batch PDF API, stable immediate .md selection and
independent atomic outputs. --output-dir is required; --overwrite and --config
are optional. No title/theme/TOC/index/recursion options or abbreviations.
Expected failed items report safe ordinal/PDF_PUBLICATION_FAILED/stage diagnostics;
preflight reports BATCH_PDF_PREFLIGHT_FAILED without counts. Success lines and
summary are buffered until runtime shutdown succeeds. Exit0 means all succeeded,
exit1 means expected partial/publication/runtime failure, parser errors exit2.
Committed files remain on cleanup failure; no rollback. Existing commands and
direct APIs are unchanged. Release 1.2.0 is not published by this change.

## Candidate acceptance

| Format | Single CLI | Batch CLI | Single / batch pipeline API |
| --- | --- | --- | --- |
| HTML | publish | publish-batch | Available |
| DOCX | publish-docx | publish-docx-batch | Available |
| PDF | publish-pdf | publish-pdf-batch | Available |

See [candidate evidence](docs/releases/1.2.0/CANDIDATE.md) for closed sprint
references, packaging/CI checks and acceptance boundaries. Preparation creates
no release/tag and does not change main.

The [publication request](docs/releases/1.2.0/PUBLICATION-REQUEST.md) stages the
GitHub release text and execution/asset-verification checklist. Opening or
merging that request does not publish the release; tag creation remains separate.
