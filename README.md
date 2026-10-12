# BGDXCarbon HTML Publisher 1.0

Publish UTF-8 Markdown as standalone HTML, individually or as a batch with an
index. Outputs include embedded light/dark styling, optional heading navigation,
and document title/language metadata. Windows and Linux with Python 3.13/3.14
are covered by CI.

## Install

Python 3.13 or newer is required. Download the wheel from
[GitHub Releases](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/releases).
In PowerShell, from the directory containing the downloaded wheel:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .\bgdxpublisher-1.0.0-py3-none-any.whl
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

## DOCX development

On the development branch, publish an editable Word document:

```powershell
bgdxpublisher publish-docx .\document.md --output .\document.docx --title "Izveštaj" --lang sr-Latn
```

DOCX supports CommonMark headings, paragraphs, emphasis, lists, quotations, code,
and HTTP/HTTPS/mailto hyperlinks. Images become plain alternative text; relative
and fragment links remain visible labels. Raw HTML remains visible text.
The title is metadata, while visible headings come from Markdown. Output uses
A4 portrait pages with 2.5 cm margins. Existing output requires `--overwrite`;
the parent directory must exist. HTML commands are unchanged.
DOCX batch export, templates and PDF are future work. DOCX is not part of the
published v1.0.0 package; install the development checkout for this command.

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

This release is an HTML command-line tool. PDF, DOCX, custom templates, remote
hosting, and a graphical interface are outside 1.0. Raw HTML is escaped; unsafe
link schemes are refused; images render as alternative text. External images
are not embedded. Outputs use no scripts or external stylesheets.

Inputs accept UTF-8 with or without BOM. Language tags support a documented
subset: language, optional Script/REGION and non-duplicate variants; private-use
and extension forms are not supported. Existing output permissions are preserved
on POSIX overwrite; new POSIX outputs use 0644. Filesystems must support hard
links for atomic no-overwrite publication. Output symlinks are refused.

See [the usage guide](docs/USER-GUIDE.md), [examples](examples/README.md),
[release notes](RELEASE-NOTES.md), and [release process](docs/RELEASING.md).
