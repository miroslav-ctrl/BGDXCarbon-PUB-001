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
4. Merge the reviewed release PR to develop after final-head CI succeeds.
   Replace the changelog release-candidate heading with the actual release date.
5. Tag the approved merged release commit with `v` followed by the package version
   (for example `v1.1.0`) and push that tag only when publication is authorized.
   The release workflow runs the reusable CI matrix before publishing the wheel,
   source distribution and SHA256SUMS.txt. Tag and package versions must match.
   A failing verification job prevents publication.
6. Confirm the GitHub release URL and attached files. This process publishes
   GitHub assets only, not PyPI. Local checkouts are not switched or cleaned.

Release preparation does not itself create a tag or publish an edition.
