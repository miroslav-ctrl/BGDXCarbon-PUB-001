# Release 1.2.0 - accepted complete CLI/API edition scope

Prepared/accepted by owner 2026-10-21 in this task. Scope accepted for release1.2.0;
SPR-021 planning Draft PR authorized separately. Implementation, version bump,
merge, tag and publication require separate authorization.
Baseline develop: `583618fc18474a3c1147e273d7c5e0262aef47d7` after completed SPR-020.
[Issue #55](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/issues/55) is completed.
[Baseline CI](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/39387903170)
passes four environments, total99.91%, nine independent >=95% package gates.

## Product and release identity

A locally installed Markdown publishing tool for Windows/Linux, usable from a
command line or Python API, producing standalone HTML, editable DOCX and
selectable-text PDF. Completion means the bounded product below, not completion
of all possible enterprise features.

Accepted target version: 1.2.0. Existing public v1.0.0/v1.1.0 are immutable; v1.1.0 was
published on2026-10-14. Do not reuse/retag it. Verify target version remains unused at release preparation;
if already used, obtain an explicit version decision before publishing. Keep current package/config/runtime versions until then.
Distribution remains GitHub wheel, source distribution and SHA256SUMS.txt;
no PyPI, installer, desktop app or hosting commitment.

## Required capability matrix

| Capability | HTML | DOCX | PDF |
| --- | --- | --- | --- |
| Single document CLI | Available, preserve | Available, preserve | Available, preserve |
| Single document pipeline API | Available, preserve | Available, preserve | Available, preserve |
| Batch pipeline API | Available, preserve | Available after SPR-020 | Required new work |
| Batch CLI | Available, preserve | Required new work | Required new work |
| Index/theme/heading navigation | Existing HTML behavior | Not required | Not required |

Preserve existing command names/options/defaults/exit behavior and both current
pipeline and legacy direct APIs. New DOCX/PDF batch command names/options and
exact diagnostics require their own approved sprint specifications; do not
reinterpret existing publish-batch (HTML) or overload its existing behavior.

## Mandatory batch behavior

- Immediate regular .md files, case-insensitive extension, stable deterministic
  source snapshot, no recursion. Input language validation and documented
  format-specific filesystem/symlink/alias/collision policy before child work.
- Each document reuses its registered single-document pipeline once, with fresh
  job/context; immutable terminal outcomes and derived success/failure counts.
- Independent atomic outputs. Explicit overwrite; source/previous bytes protected
  on refusal/precommit failure. Continue expected per-document failures; safe
  counts/status/stage diagnostics. No fabricated whole-batch success.
- Unexpected external failure propagates/stops later attempts; earlier commits
  remain. Postcommit cleanup failure reports failed outcome while file remains;
  no batch rollback or arbitrary concurrent filesystem guarantee.
- Runtime ownership and close-once/primary-error behavior explicitly specified
  and tested for each new CLI, using established runtime/CLI conventions.
- New batch CLI: success exit0, expected publication/preflight/partial failure
  exit1, parser error exit2; exact stdout/stderr/error contracts fixed by plan.
  Do not leak paths/content/raw causes through safe operational diagnostics.
- DOCX/PDF batch creates no index/manifest and adds no title/theme/TOC/template
  option. Filename stem and language map to existing single-document metadata.
  Existing HTML index/theme/navigation behavior remains unchanged.
- Same rendering and metadata semantics as single-document APIs, including
  documented Unicode/BOM, image-as-alt-text and supported PDF glyph limitations.

## Required quality and evidence

1. Windows/Linux, Python3.13/3.14 CI: Ruff/Black/MyPy/full tests and total coverage
   >=99%. Preserve existing nine independent >=95% gates; add an independent
   >=95% gate for any new PDF batch pipeline package. Explain legitimate skips
   and execute filesystem-sensitive cases on a supported CI environment.
2. Fresh installed distribution outside checkout with source PYTHONPATH removed:
   actual existing/new commands and APIs; success/refusal/overwrite/mixed/all
   failures/preflight/status/metadata and runtime cleanup regressions.
3. DOCX OOXML member and PDF semantic fidelity against individual pipelines under
   identical dependencies. Narrowly document any unavoidable volatile fields;
   do not replace semantic assertions with whole-file byte equality.
4. Real DOCX/PDF batch artifact evidence with >=2 different inputs each; include
   a multipage PDF case. Render and inspect every page in the acceptance samples,
   record exact commit/run/artifact/digest and inspection scope. Retain existing
   visual/API/CLI checks.
5. Every sprint has approved acceptance, formal review, separately authorized
   merge, exact post-merge CI and accepted closure before issue completion.
   Automated self-review is disclosed as COMMENT, not independent human approval.

## Required documentation and release acceptance

- README/USER-GUIDE/examples show all supported commands and API entry points,
  installation, supported platforms, errors/exit codes, overwrite/partial failure,
  runtime ownership and rendering/filesystem limitations.
- Fix current stale user-facing statements: README says all DOCX batch is future
  work despite existing API; release guide still describes eight rather than nine
  current gates. Preserve historical v1.1.0 release notes as history; add a distinct
  next-version section and changelog entry instead of rewriting published scope.
- Version assertions/package/runtime/default configurations and example commands
  agree at release preparation. Build/install verified wheel and source archive;
  verify packaged configuration/fonts/license material and asset checksums.
- Final release-candidate acceptance links to closed sprint evidence and lists no
  unresolved blocking findings. Owner accepts the exact release candidate.
- Only after explicit publication authorization: tag the approved develop commit,
  run existing release workflow, verify attached assets and fresh download/install.
  No main change is required. Release prep alone never creates a tag/release.

## Delivery sequence and stopping rule

| Work package | Deliverable | Completion boundary |
| --- | --- | --- |
| SPR-021 | DOCX batch CLI over completed SPR-020 API, user docs/examples | Approved plan, implementation, exact CI, accepted closure |
| SPR-022 | PDF batch pipeline API reusing single PDF service | Approved contracts/tests/coverage/installed and visual evidence, accepted closure |
| SPR-023 | PDF batch CLI over accepted batch API, docs/examples | Approved error/runtime contracts, regression/installed checks, accepted closure |
| Release preparation | User-doc alignment, versioning, final cross-format candidate acceptance | Approved candidate with successful exact CI |
| Authorized publication | GitHub tag/release/assets and installed download verification | Published assets verified, final release evidence accepted |

Sprint numbers are proposed allocation; check availability before opening work.
No dates or duration are committed by this scope. Existing HTML and single DOCX/PDF
support, including their completed migrations, is preserved rather than rebuilt.

The edition is complete when every required matrix cell and quality/doc/release
condition above is satisfied. Do not add another feature sprint to this edition
without an explicit scope decision. New requests become later-edition backlog
unless they are fixes required to meet an already accepted criterion.

## Deferred beyond this edition

GUI/web editor/hosting/cloud API, accounts/authentication/multitenancy, remote
storage/connectors, custom templates/themes for binary formats, embedded images,
DOCX/PDF indexes/TOC/PDF-UA, recursive discovery, PDF/DOCX input conversion,
persistent job queues/workers/database, retries/cancellation/concurrency,
whole-batch transactions/rollback and new publishing/distribution channels.

These are not conditions for completing this bounded CLI/API edition. General
product branding as Enterprise Publisher Suite does not imply these capabilities.

## Review and execution boundary

Owner acceptance fixes this edition scope; it is not blanket authorization to
implement all work packages, merge, publish or alter main. SPR-021 is planned in
[docs/sprints/SPR-021](sprints/SPR-021/SPR-021.md) as documentation only. Subsequent
implementation requires separate authorization after plan review/merge. Preserve
sources/ reference files.
