# Publisher Suite release process

1. Synchronize package, runtime and both default configuration versions.
   Update version assertions in CLI tests and installed-wheel CI.
2. Review release notes, examples and documentation for HTML, DOCX, PDF and
   publisher core. Confirm HTML/batch HTML/DOCX/batch DOCX pipeline command
   integration and single/batch PDF pipeline CLI/API integration;
   verify direct legacy APIs remain intact.
3. Pass Ruff, Black, MyPy, all tests, total coverage >=99%, and separate domain,
   jobs, pipeline, orchestration, html_pipeline, batch_pipeline, docx_pipeline,
   pdf_pipeline, docx_batch_pipeline and pdf_batch_pipeline coverage >=95% each
   (ten independent gates). Verify installed-wheel HTML/DOCX/PDF commands, batch DOCX CLI/API
   and single/batch PDF CLI/APIs on Windows/Linux with Python 3.13/3.14. Review CI DOCX/PDF
   and distinct PDF pipeline single/multipage, batch DOCX API and batch DOCX CLI
   and distinct batch PDF API and CLI single/multipage preview artifacts; inspect all
   acceptance sample pages.
4. Obtain owner acceptance of the exact candidate and separately authorize merge
   into develop after final-head CI succeeds. Keep the candidate marked unpublished
   until publication is separately authorized; record the actual date only then.
5. Tag the approved merged release commit with `v` followed by the package version
   (for example `v1.2.0`) and push that tag only when publication is authorized.
   The release workflow runs the reusable CI matrix before publishing the wheel,
   source distribution and SHA256SUMS.txt. Tag and package versions must match.
   A failing verification job prevents publication.
6. Confirm the GitHub release URL and attached files. This process publishes
   GitHub assets only, not PyPI. Local checkouts are not switched or cleaned.

Release preparation does not itself create a tag or publish an edition.

## Candidate checks without publication

See releases/1.2.0/CANDIDATE.md. Build both archives with `python -m build`;
default build creates the wheel from the source archive. Run
`python tools/verify_distributions.py dist-review` to verify versions, source/
wheel/sdist package bytes, configuration, fonts/license material and checksums.
CI then exercises the complete existing CLI/API smoke against BOTH fresh wheel
and source-archive installs outside checkout; source PYTHONPATH is removed.
Download candidate-distributions artifacts for each platform/Python and verify
SHA256SUMS.txt. Archive checksums identify that build; different timestamps may
produce different archive hashes across builds, so use exact artifact provenance.
A successful candidate CI is not authorization to merge, tag or publish.

The current1.2.0 publication proposal is in
[PUBLICATION-REQUEST.md](releases/1.2.0/PUBLICATION-REQUEST.md). It records the
accepted candidate, exact post-merge CI, staged notes and remaining authorization/
date/tag/public-asset/download gates. A request PR is not publication permission.
