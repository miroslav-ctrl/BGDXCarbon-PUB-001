# SPR-003 Implementation Specification

## Contracts

`PublishRequest` and `PublishResult` are frozen dataclasses. `PublishingService`
accepts one request and returns the absolute output path and encoded byte count.
`PublishingError` describes expected input, rendering and filesystem errors.
The initialized runtime registers this service with its existing logger.

CLI parsing delegates to `run_publish`. The adapter initializes and starts the
application, resolves the publisher, and closes the runtime in a finally block.
It reports expected failures without traceback and only announces success after
cleanup succeeds. Unexpected programming exceptions propagate after cleanup.

## Renderer

Use markdown-it-py CommonMark parsing with raw HTML disabled. Link destinations
allow only relative URLs, HTTP(S), and mailto, in addition to the library's
unsafe link checks. Image tokens are
converted to escaped alternative text. HTML title is escaped. Embedded CSS and
a restrictive content security policy provide a standalone readable document.
No plugins or external assets are used.

## Filesystem

Read input strictly as UTF-8 and render before creating any output. A temporary
file in the target parent receives the complete document, is flushed and fsynced,
then closed. Explicit overwrite uses os.replace. Without overwrite, os.link
atomically creates the destination only if absent, preventing a concurrent
writer from being overwritten. Filesystems without hard-link support fail
explicitly; there is no unsafe fallback. Temporary files are removed in finally.

The transaction covers rendering and output commit. It does not roll back an
already committed output if subsequent runtime cleanup fails. Atomic replacement
does not provide a power-loss durability guarantee. Directory permissions and
concurrent changes to user-controlled directory trees remain OS responsibilities.

## Review corrections

Image labels render as escaped text even when inline destinations use rejected
schemes. Ordinary links retain the scheme allowlist. Unknown document language
is tagged `und` rather than assuming Serbian. On POSIX, new HTML is explicitly
created with mode 0644; overwrite preserves the existing destination mode.
