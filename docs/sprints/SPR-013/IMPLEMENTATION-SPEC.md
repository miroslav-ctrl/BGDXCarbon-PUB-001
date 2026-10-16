# SPR-013 Implementation Specification

## Dispatch and result contract

Keep run_publish signature and argparse configuration unchanged. Preserve PDF-first, DOCX-second dispatch behavior. In the HTML branch resolve HtmlPublicationService from PublisherApplication.context.services and call publish with the existing PublishRequest values in their existing order.

Adapt HtmlPublicationResult.publication into the existing PublishResult-shaped CLI success path. Preserve exactly one stdout line: Published: <output path>, followed by newline, and exit 0. Do not invoke legacy PublishingService.publish as fallback or duplicate publication. Do not print job metadata on stdout.

## Error mapping

Catch HtmlPublicationError explicitly at the CLI boundary: it is a PublisherDomainError and must not be assumed to belong to RuntimeFoundationError. Keep runtime initialization/shutdown and legacy DOCX/PDF error handling compatible.

For HTML pipeline failure, produce one primary stderr line:
Publication failed: HTML_PUBLICATION_FAILED stage=<stage_name>
Return 1. Obtain stage_name from the structured failed pipeline result; never traverse or stringify the exception cause to build user output. The fixed internal pipeline stage names are validate, read, render, write and cleanup. Do not expose Markdown, rendered HTML, user title, raw source paths from exceptions or traceback. Success output may contain the requested output path as before.

This intentionally replaces legacy raw operational exception text for the HTML command. Do not promise exact legacy failure-message equivalence. Document the code/stage meaning and advise checking input/options/permissions without exposing exception messages.

Argparse continues rejecting invalid metadata/options with exit 2 and existing precise validator diagnostics before runtime publication. No parser error is converted to exit 1. Operational problems after parsing return 1.

Unexpected programming exceptions retain existing propagation behavior; this sprint does not silently swallow arbitrary exceptions.

## Runtime lifecycle and cleanup

Initialize/start once and close configured/running runtime in finally on both success and expected publication failure. A primary publication failure remains primary if shutdown also fails. Preserve Runtime cleanup failed reporting for runtime errors; do not stringify HtmlPublicationError causes in that path.

A shutdown failure after successful publication returns 1 and must not print Published success. The committed file remains. Pipeline cleanup failure likewise returns 1 with stage=cleanup even if the writer already committed output. Do not delete or restore committed files as rollback.

## Compatibility boundaries

Leave publish-docx, publish-pdf and publish-batch routing unchanged. Retain PublishingService public contracts for direct API users. Existing defaults for title/lang/theme/TOC, UTF-8/BOM, overwrite and source/alias/symlink/race protections continue through HtmlPublicationService.

Logging from the new HTML route retains SPR-012 safe-log policy. Do not add raw error logging or diagnostics from __cause__. Existing other-command logging is outside this sprint.

## Tests and CI

Service-selection tests must register/patch the new service and make legacy HTML publication fail if invoked. Differential tests compare existing expected HTML with CLI output over metadata/theme/TOC and Unicode/BOM inputs. Exercise parser exit 2, operational exit 1, runtime start/stop failures, simultaneous publication/shutdown failure and postcommit cleanup failure.

Extend installed-wheel checks outside checkout for actual publish success, refusal without overwrite, explicit overwrite and invalid metadata. Assert safe stderr on expected operational failure. Keep all four OS/Python jobs and independent package coverage gates. No new package coverage threshold is needed for CLI changes.
