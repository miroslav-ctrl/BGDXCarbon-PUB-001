# BGDXCarbon Publisher Suite 1.1.0

Adds DOCX and PDF publishing and a typed publisher core to the existing HTML CLI.

- `publish-docx`: editable Word documents with Unicode, metadata, headings,
  inline formatting, lists, quotations, code and safe external links.
- `publish-pdf`: selectable Latin/Cyrillic text, embedded licensed DejaVu fonts,
  A4 layout, automatic pagination, metadata and safe external links.
- Immutable document models, structured validation and controlled job lifecycle.
- Deterministic sequential pipelines with typed stage contracts, callable stage
  validation, failure causes, reverse-order cleanup and safe structured logs.
- Independent coverage gates of at least 95% for domain, jobs and pipeline.

Existing HTML, batch, index, theme, table-of-contents and diagnostics commands
remain available. Binary outputs use atomic writes and explicit `--overwrite`.
The publisher core is an in-process API and does not yet orchestrate rendering.

Python 3.13+ is required. CI covers Windows/Linux and Python 3.13/3.14.
Package, runtime and default configuration versions are synchronized to 1.1.0.
Install the release wheel with `python -m pip install PATH_TO_WHEEL`.
GitHub release assets are the wheel, source distribution and SHA256SUMS.txt.
No PyPI publication is included.

Limits: no DOCX/PDF batch export, custom templates, embedded document images,
recursive scans, hosting or graphical UI. PDF has no contents navigation or
PDF/UA tagging. Unsupported PDF glyphs fail explicitly. New publication without
overwrite requires filesystem hard-link support. HTML batch publication retains
successful files after individual failures. Language validation uses a subset
of BCP 47 rather than registry-based validation.
