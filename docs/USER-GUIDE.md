# HTML Publisher usage guide

## Source documents

Save Markdown as UTF-8; a UTF-8 BOM is also accepted. CommonMark supports
headings, paragraphs, emphasis, lists, links, quotes, and fenced code. Literal
HTML remains visible text. Images become plain alternative text, including
formatted labels. Link destinations permit relative URLs, HTTP(S), and mailto.
This is not a browser sanitizer for arbitrary HTML documents.

Title validation rejects empty/whitespace-only text and control characters.
Language values include `sr-Latn`, `sr-Cyrl`, `en`, `en-US`, and `und`.
Values such as `en_US` and repeated variants fail argument validation with a
diagnostic. `--title` is available only for single-document publication.

## Heading navigation

`--toc` includes source headings in document order. Labels preserve plain text;
targets are unique even for repeated headings. Unicode links are encoded. A
document with no headings adds no navigation. The caption is `Contents`.

## Batch and index

Create the source directory and add `.md` files before running `publish-batch`.
Selection is deterministic by case-folded filename, then filename. Case-insensitive
destination collisions are rejected on every platform. Symlink source files
follow the single-document source behavior; output symlinks are rejected.

For example, with `a.md` and `b.md`, a successful batch reports
`Batch complete: 2 published, 0 failed.` With `--index`, it also reports
`Index published: ...index.html`. Click each link in the index to open its
matching document. Special filename characters are escaped in labels and encoded
in URLs; they are not interpreted as Markdown.

Invalid UTF-8, unreadable sources, existing output without overwrite, or other
expected per-document errors are reported individually, and later files continue.
The index excludes unsuccessful documents and stale existing HTML. If all source
documents fail, the generated index explicitly says no documents succeeded, and
the exit code remains 1. Empty input is a preflight error and creates no index.

## Troubleshooting

| Symptom | Action |
|---|---|
| `invalid choice` for a command/option | Check `version` and `--help`; install the correct wheel or switch the editable checkout to the intended branch. |
| Input directory not found | Create it and add Markdown files; batch only creates output directories. |
| Output exists | Choose another output path or explicitly pass `--overwrite`. |
| Existing index blocks a batch | Pass `--overwrite` or choose a new output directory. |
| `index.md` conflict | Rename that input or omit `--index`. |
| Browser still shows an older page | Confirm the opened path and refresh. A changed tab title does not change Markdown headings. |
| Atomic no-overwrite commit fails | Use a filesystem that supports hard links; inspect the reported OS error. |
| Configuration/runtime failure | Run `doctor` and `config validate --config PATH`. |

The application cannot guarantee isolation from concurrently changed directories
or machine power loss. Keep source files separately backed up. Existing files
are replaced only when overwrite is explicitly requested.

## Word output on the development branch

Install the updated checkout with `python -m pip install -e ".[dev]"` to include
the new DOCX dependency. The v1.0.0 release package contains only HTML commands.

```powershell
bgdxpublisher publish-docx .\examples\docx-sample.md --output .\sample.docx --title "Izveštaj" --lang sr-Latn
```

The output parent must exist; choose a `.docx` filename. Repeat with `--overwrite`
to replace it. Open the resulting document in Word or a compatible reader.
Heading text comes from Markdown; `--title` sets document properties. Word
heading styles remain editable. Lists preserve starting numbers and nesting.
The parser treats consecutive ordered items as one list even when source numbers
restart; separate them with a paragraph or another block to create a new list.

HTTP(S) and mailto links are active. Relative and fragment links are visible
labels without a destination. Images become text; raw HTML stays literal.
DOCX has a fixed print layout without `--theme`, `--toc` or batch/index options.
Code retains indentation and uses a monospace font, without syntax highlighting.
The command uses the same configuration and exit codes as HTML publishing.

## PDF output on the development branch

After installing the updated checkout with `python -m pip install -e ".[dev]"`:

```powershell
bgdxpublisher publish-pdf .\examples\pdf-sample.md --output .\sample.pdf --title "Izveštaj" --lang sr-Latn
```

This command renders Markdown directly, without converting the DOCX or HTML
outputs. ReportLab and licensed DejaVu fonts are packaged with the application;
publication does not install applications, fetch images or use machine fonts.
The PDF contains selectable text with embedded font subsets and Unicode maps.
Supported glyphs include Serbian Latin and Cyrillic. An unsupported character
reports its Unicode code point and leaves the previous output intact.

PDF supports CommonMark headings, paragraphs, emphasis, ordered and bullet lists,
quotes, inline/fenced/indented code and HTTP(S)/mailto links. Relative/fragment
links remain labels; images become text and raw HTML remains visible text.
PDF paragraphs collapse ordinary source whitespace; hard breaks are preserved.
Code expands tabs to four spaces, preserves line breaks, and wraps long lines.
Pagination is automatic; headings stay with following content when space allows.

Use a `.pdf` output path with an existing parent directory; repeat with
`--overwrite` to replace it. Title and language are PDF metadata. The layout is
A4 portrait with 2.5 cm margins, without dark themes, contents or batch/index
options. Metadata language and selectable Unicode are not a PDF/UA conformance
claim. Invalid CLI arguments return 2; publication or runtime failure returns 1.

The published v1.0.0 assets remain unchanged. PDF is currently a development
feature based on the DOCX sprint; follow the PR dependency before merging.

## Configuration

Default configuration is packaged. `configs/default.yaml` is a sample equivalent.
`--config` accepts a YAML file. Application identity, runtime environment, and
logging settings are validated; unrecognized settings are rejected. To suppress
console logging, use a configuration with `logging: {console: false}`.

## HTML pipeline diagnostics

The publish command uses the HTML job pipeline. Successful output remains Published: <path>. Parser errors retain exit code 2 and precise metadata diagnostics. Operational HTML failures return 1 with Publication failed: HTML_PUBLICATION_FAILED stage=<stage>. Stages are validate, read, render, write and cleanup. Check input/options/output permissions for the reported stage. Raw exception messages and document content are not printed by this diagnostic; safe identifier/code logs may also appear on stderr.

A cleanup or runtime shutdown failure after atomic commit can return 1 while the committed file remains. No automatic rollback is performed. The direct legacy PublishingService API retains its route.

### DOCX pipeline Python API

For Python integrations, `bgdxpublisher.docx_pipeline.DocxPublicationService`
is registered alongside the existing DOCX service. Its `publish(DocxRequest)`
returns an immutable `DocxPublicationResult` containing `publication` and job
`execution`, or raises `DocxPublicationError` with code `DOCX_PUBLICATION_FAILED`
and a structured failed execution. The new route logs safe codes/stages/IDs;
internal causes are retained for debugging. A cleanup failure after commit can
leave a DOCX file while reporting FAILED; no rollback is promised. See
`examples/docx_pipeline.py`. Direct `DocxPublishingService` behavior and
diagnostics are unchanged.

### DOCX CLI diagnostics

`publish-docx` now uses the registered DOCX job pipeline. Options and successful
stdout remain unchanged: `Published: <output path>` and exit 0, only after runtime
shutdown succeeds. Expected operational failures return 1 with one primary line:
`Publication failed: DOCX_PUBLICATION_FAILED stage=<stage>`.
Stages are `validate`, `read`, `render`, `write` and `cleanup`. Safe job/code logs
may additionally appear on stderr. Raw paths, document content and cause messages
are not included in this new publication diagnostic. Check input/options/output
permissions for the indicated stage. Parser errors retain precise diagnostics and
exit 2; a valid command naming a nonexistent source is operational exit 1.

If runtime shutdown also fails, `Runtime cleanup failed:` appears first, followed
by the original publication diagnostic; shutdown does not replace the DOCX failure.
A shutdown failure after successful publication returns 1 with the existing runtime
failure diagnostic and no `Published:` stdout. Existing runtime/config error
formats are unchanged and outside the safe publication-message contract.
Cleanup/shutdown can fail after a DOCX was committed: the file remains, with no
rollback. Both direct Python APIs retain their existing contracts. PDF, HTML and
batch command behavior and PDF-first dispatch precedence are unchanged.

### Batch pipeline diagnostics

`publish-batch` uses the registered batch HTML job pipeline. Command options and
successful `Published:`, `Batch complete:` and `Index published:` stdout lines
are unchanged. Expected failures return 1 and use these stderr diagnostics:

- `Batch publication failed: BATCH_HTML_PREFLIGHT_FAILED` for batch preflight.
- `Failed: item=<ordinal> HTML_PUBLICATION_FAILED stage=<stage>` for a document.
  Ordinals start at 1 in deterministic discovery order, including failed items.
- `Index publication failed: BATCH_INDEX_FAILED` for independent index failure.

Stages are `validate`, `read`, `render`, `write` and `cleanup`. Check the input,
options and output permissions for that stage. These diagnostics intentionally
replace raw source paths/exception messages; safe code/job logs may also appear.
Parser errors, such as missing arguments or invalid language/theme, still return
2. A valid command naming a nonexistent input directory returns preflight exit 1.
Existing configuration/runtime diagnostics keep their current format.

Expected document failures continue to the next item. Summary counts include
documents only; index failure does not add a failed document. An index includes
COMPLETED jobs only, even if a failed cleanup left a file on disk. An all-failed
batch may produce a valid empty index and still returns 1.

Batch stdout is buffered until runtime shutdown succeeds. If shutdown fails,
exit is 1 and no buffered publication/summary/index stdout is emitted; primary
publication diagnostics and `Runtime cleanup failed:` remain available. Already
committed files remain; inspect the output directory before retrying and use
`--overwrite` only when replacement is intended. Directory creation during
preflight is not transactional. No automatic rollback is promised. The legacy
direct `publishing.batch.publish_batch` Python API remains unchanged.

### PDF pipeline Python API

The runtime registers `bgdxpublisher.pdf_pipeline.PdfPublicationService` alongside
legacy `PdfPublishingService`. Call `publish(PdfRequest(...))` to obtain frozen
`PdfPublicationResult(publication, execution)` with a completed job. Each call
has independent job/context IDs and validate/read/render/write stages.
`PdfPublicationError` has fixed string/code `PDF_PUBLICATION_FAILED`; obtain stage
from `error.result.pipeline_result.failure.stage_name`. Safe new-route logs contain
codes/stages/IDs; internal causes remain available for debugging. Caller owns
initialize/start/try-finally-stop; the service does not close the runtime.

Postcommit cleanup may fail with FAILED/stage=cleanup and no successful result
while retaining the committed PDF; no rollback is promised. Unsupported glyphs,
font and layout failures are render-stage failures. Direct `PdfPublishingService`
retains its diagnostics and behavior, including raw legacy error details.
The `publish-pdf` CLI uses the pipeline with the diagnostics below.
See `examples/pdf_pipeline.py`; optional output directory retains single/multipage
samples. PDF pipeline API does not add batch export, templates or dependencies.

### PDF CLI diagnostics

`publish-pdf` uses registered `PdfPublicationService`. Options/defaults and success
stdout remain `Published: <output path>` plus newline, exit 0 only after successful
runtime shutdown. Expected operational failure returns 1 with exactly one primary
`Publication failed: PDF_PUBLICATION_FAILED stage=<stage>` line; safe job/code logs
may also appear on stderr. Stages: validate, read, render, write and cleanup.
Missing source/invalid extension/output policy is validate; invalid UTF-8 is read;
unsupported glyph/control/font/layout is render. Raw path/content/cause and glyph
code are omitted from this publication diagnostic. Inspect source characters or
use the direct API's internal cause for debugging; legacy direct API still retains
its original glyph-code/error behavior. Parser invalid/missing arguments retain
precise diagnostics and exit 2 before runtime. Runtime/configuration messages keep
existing formats and are outside the safe publication-message contract.

Expected runtime shutdown failure emits `Runtime cleanup failed:` before the
original publication diagnostic; one primary line and no Published stdout. After
successful publication, expected stop failure returns 1 with the existing runtime
failure diagnostic. Unexpected active PDF exception survives unexpected shutdown
with a fixed safe note; unexpected shutdown without an active unexpected primary
(including already handled typed publication failure) propagates. These are
programming exceptions, not safe operational exit-1 diagnostics. Pipeline cleanup
failure reports stage=cleanup; internal writer errors remain write. Cleanup/stop
failure may retain an already committed PDF: no rollback is promised. Other command
contracts and PDF-first precedence remain unchanged.
