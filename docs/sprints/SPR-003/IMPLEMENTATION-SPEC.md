# SPR-003 Implementation Specification

## Publisher core extension

The repository's existing EAS 1.0 architecture document is not present in the
reviewed tree. The available SPR-001/SPR-002 specifications establish module
boundaries: runtime composes configuration, logging, and the typed service
registry; domain behavior remains in focused packages. The pre-existing SPR-003
specification defines shipped Markdown-to-HTML behavior. This extension is
additive and preserves that behavior and the public CLI contract.

`bgdxpublisher.domain` owns frozen `Document` and `DocumentRequest` models,
`DocumentType`, structured `ValidationIssue`/`ValidationResult` values, and
document validation. Identifiers are UUIDs; types are `markdown`, `html`, `pdf`,
and `docx`; metadata accepts finite JSON values only and is recursively frozen.
Creation timestamps must be timezone-aware and are normalized to UTC.

`bgdxpublisher.jobs` owns frozen job requests and `PublisherJob` models,
`JobStatus`, `JobLifecycle`, and `JobService`. Lifecycle transitions return a
new immutable job and follow `CREATED → VALIDATED → QUEUED → RUNNING →
COMPLETED`, with controlled transitions to `FAILED` from nonterminal states.
Document and job validators return stable error codes; model/service failures
retain their structured validation result.

`bgdxpublisher.pipeline` owns the `PipelineStage` protocol, per-run
`PipelineContext`, `PipelineResult`, and `PipelineEngine`. The engine snapshots
the declared sequence, validates stage names and connected input/output types,
then executes stages serially. Contract and stage failures raise
`PipelineExecutionError` with a failed result, no output, completed-stage names,
and the original exception as `__cause__`. Context cleanup runs in reverse
registration order; all cleanup errors are included in the failure result.
Empty pipelines return the input unchanged.

Services accept the existing standard-library logger, logging job identifiers,
stage names, status/error codes, and outcomes only. Document values and
exception messages are not included in pipeline logs. The pipeline performs no
filesystem, network, database, rendering, or external publishing operations.

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
