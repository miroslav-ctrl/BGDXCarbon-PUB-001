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

## Configuration

Default configuration is packaged. `configs/default.yaml` is a sample equivalent.
`--config` accepts a YAML file. Application identity, runtime environment, and
logging settings are validated; unrecognized settings are rejected. To suppress
console logging, use a configuration with `logging: {console: false}`.
