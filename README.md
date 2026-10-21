# BGDXCarbon Publisher Suite 1.1

Publish UTF-8 Markdown as standalone HTML, editable DOCX, or selectable-text PDF.
HTML supports individual and batch publication with an index. Outputs include embedded light/dark styling, optional heading navigation,
and document title/language metadata. Windows and Linux with Python 3.13/3.14
are covered by CI.

## Install

Python 3.13 or newer is required. Download the wheel from
[GitHub Releases](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/releases).
In PowerShell, from the directory containing the downloaded wheel:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .\bgdxpublisher-1.1.0-py3-none-any.whl
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
The development branch includes `publish-docx-batch` and its registered Python API;
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
Cyrillic support. Unsupported glyphs fail with their Unicode code point instead
of being silently replaced. Images become alternative text; raw HTML is literal
text, and relative/fragment links remain plain labels. Existing output requires
`--overwrite`, and the parent directory must exist. The title is metadata only.
HTML and DOCX commands retain their existing behavior. The development branch
includes a batch PDF Python API; batch PDF CLI remains future SPR-023 work.
Custom templates, embedded images, contents navigation and PDF/UA tagging remain
outside this foundation scope. PDF is included in version 1.1.0; the older v1.0.0 package supports HTML only.

## Publisher core API

`bgdxpublisher.domain` provides immutable document descriptors and structured
validation. `bgdxpublisher.jobs` provides immutable jobs and controlled lifecycle
transitions. `bgdxpublisher.pipeline` executes explicitly typed stages in order,
reports failures with their causes, and runs registered cleanup in reverse order.
The core is an in-process API. Registered HTML, batch HTML, DOCX, batch DOCX, PDF and batch PDF pipelines
serve existing commands where provided; batch PDF currently has an API only.
Direct legacy services remain available with their
original contracts; publish-pdf operational failures use safe code/stage diagnostics.
See examples/pdf_pipeline.py for installed API verification.

## Commands and diagnostics

- `publish`, `publish-batch`: Markdown publishing; use `--help` for arguments.
- `version`: application version, Python version, environment.
- `doctor`: configuration, logging, runtime, and workspace diagnostics.
- `config validate`: validate configuration; `runtime status`: initialize and inspect runtime.
- `--config PATH` is available on publishing, doctor, config validate, and runtime status.

Exit status: 0 means success, 1 means runtime/publication failure, 2 means invalid
CLI arguments. Logs go to stderr by default; success reports go to stdout.
No-argument invocation retains runtime startup diagnostics.

## Scope and output policy

Version 1.1.0 supports HTML, DOCX and PDF; the historical 1.0 release was HTML-only.
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

## Batch DOCX (development, planned for 1.2.0)

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
and direct APIs retain their contracts. This does not publish release1.2.0.

## Batch PDF API (development, planned for 1.2.0)

Resolve `BatchPdfPublicationService` from an initialized/started runtime, then call
`publish(BatchPdfRequest(source_dir, output_dir, overwrite=False, language="und"))`.
Caller owns finally-stop. See examples/pdf_batch_pipeline.py for a complete
installed API example. No new batch PDF command is provided in this sprint.

The API freezes immediate .md inputs in stable order, validates all source/output
symlinks/aliases/collisions before mkdir/child publication, and reuses the registered
single PDF pipeline. Expected item failures continue, including unsupported glyphs;
results expose ordered immutable terminal executions and derived counts. Safe
preflight error is BATCH_PDF_PREFLIGHT_FAILED; per-item structured stage details
remain available. Each output is independently atomic; failed cleanup can retain
committed files and there is no batch rollback. Existing direct APIs/CLI unchanged.
