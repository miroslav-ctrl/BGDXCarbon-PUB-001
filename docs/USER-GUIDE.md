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
