# HTML 1.0 release process

1. Update package, runtime, and both default configuration versions together.
   Update version assertions in CLI tests and installed-wheel CI.
2. Review release notes, examples, user guide, and the agreed HTML-only scope.
3. Pass Ruff, Black, MyPy, pytest coverage >=99%, and installed-wheel checks on
   Windows/Linux with Python 3.13/3.14. Build both wheel and source distribution.
4. Merge the reviewed release PR to develop only after final-head CI succeeds.
5. Tag the merged commit `v1.0.0` and push that tag. The release workflow runs
   the full reusable CI matrix before publishing a GitHub release containing the
   wheel, source distribution and SHA256SUMS.txt. The tag must match package
   metadata. A failing verification job prevents release publication.
6. Confirm the published release URL and attached files. Do not claim a PyPI
   release: this process publishes GitHub assets only.

Previously confirmed browser acceptance covers the unchanged HTML rendering.
Local user checkouts are not switched or cleaned by release preparation.
