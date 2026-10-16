# SPR-012 Implementation Specification

## Public API and ownership

Add bgdxpublisher.html_pipeline exporting HtmlPublicationService, HtmlPublicationResult and HtmlPublicationError. Use a separate package so its >=95% coverage gate is independent of legacy publishing coverage.

Proposed API: HtmlPublicationService(logger: Logger).publish(request: PublishRequest) -> HtmlPublicationResult.
Construct an immutable per-service pipeline of stateless stages and a JobExecutionService using JobService and the same logger. Internal constructor injection of renderer/writer dependencies may support testing; it must not introduce global mutable state.

HtmlPublicationResult is a frozen, slotted envelope containing publication: PublishResult and execution: JobExecutionResult. Require COMPLETED execution and a pipeline output matching publication. It promises envelope immutability, not deep immutability of arbitrary external objects.

For every typed PublishRequest, create a Document descriptor (MARKDOWN, nonempty stable descriptor title/source reference) and a job; transition CREATED -> VALIDATED -> QUEUED with JobService before execution. Descriptor construction must not validate publication title/lang or read the source: publication validation belongs in the first stage. VALIDATED here means the descriptor/job are valid; the publish request still undergoes stage validation. The returned execution history retains the SPR-011 QUEUED/RUNNING/terminal convention.

HtmlPublicationError is a PublisherDomainError with stable HTML_PUBLICATION_FAILED code and the failed JobExecutionResult. Raise it from JobExecutionError, preserving the entire pipeline/original cause chain. Invalid typed request values such as title/lang/path policy errors become typed stage failures. Arbitrary objects violating the PublishRequest Python type are outside the contract.

## Stage contracts

Use frozen slotted payload dataclasses; snapshot validated request options rather than retaining mutable stage state.

| Stage | Input -> output | Behavior |
| --- | --- | --- |
| validate | PublishRequest -> ValidatedHtmlRequest | Validate title/lang/theme and path/overwrite rules; determine default title from source stem |
| read | ValidatedHtmlRequest -> HtmlSource | Read once using utf-8-sig; carry validated options |
| render | HtmlSource -> RenderedHtml | Render once with existing HtmlRenderer, preserving title/lang/theme/TOC |
| write | RenderedHtml -> PublishResult | Encode UTF-8 once and commit once with existing atomic writer |

Validate source regular-file existence, input/output alias protection (including samefile), output symlink refusal, output parent existence and regular-file/overwrite policy. Reuse existing helpers or minimally extract common helpers with legacy regression tests. Retain write-time no-overwrite race protection; preflight validation alone is insufficient.

Stage validation must not write output. Reading/rendering must not perform publishing side effects. The final stage reports the encoded byte count and committed output path. Do not implement this as one stage that calls the entire existing PublishingService.publish flow.

## Failure and commit boundary

Stage failures use existing pipeline stage/input/output/cleanup codes, with stage_name identifying the operation. JobExecutionService owns transitions; PipelineEngine owns reverse-order cleanup. Preserve causes; no partial PublishResult is returned on failure.

The atomic filesystem commit is an irreversible boundary within this API. Before commit, errors preserve existing output and source; temporary resources must be removed. A successful commit followed by cleanup failure reports FAILED with no output result, but the committed file remains. Never claim rollback or delete/restore a committed destination automatically. Tests must distinguish job outcome from filesystem state. An OS failure after a successful link/replace can likewise leave committed output; document this limitation.

Reuse PublishingService.write_bytes cleanup and race protection. Register only resources actually owned by a stage, and do not close context twice. No new fallible post-commit validation stage.

## Logging and compatibility

Log job/stage identifiers and stable codes only in the new path; do not call legacy publish logging that emits paths/raw exception messages. Never log Markdown, rendered HTML, source paths, title values or raw exception messages. Preserve internal causes for callers.

Register HtmlPublicationService in PublisherApplication alongside existing services. Do not replace the default empty PipelineEngine/coordinator or change existing CLI routes. Separate service calls have independent contexts and jobs.

Output equivalence is byte-for-byte against legacy PublishingService for identical requests and input bytes, including safe Markdown handling and all existing metadata/theme/TOC options. Existing public contracts and version remain unchanged.
