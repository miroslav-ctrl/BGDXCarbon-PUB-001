# Publisher Suite release process

1. Synchronize package, runtime and both default configuration versions.
   Update version assertions in CLI tests and installed-wheel CI.
2. Review release notes, examples and documentation for HTML, DOCX, PDF and
   publisher core. For 1.1.0, confirm that the core remains an in-process API
   and does not yet connect job execution to rendering.
3. Pass Ruff, Black, MyPy, all tests, total coverage >=99%, and separate domain,
   jobs and pipeline coverage >=95%. Verify installed-wheel HTML/DOCX/PDF commands
   on Windows/Linux with Python 3.13/3.14. Review CI DOCX/PDF preview artifacts.
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
