# Branch protection (`main` and `develop`)

Recommended GitHub settings for `main` and `develop`:

1. Require a pull request before merging.
2. Solo-maintainer mode: do not require approvals before merging.
3. Require conversation resolution before merging.
4. Dismiss stale approvals when new commits are pushed.
5. Restrict direct pushes to protected branches.
6. Optionally require status checks to pass before merging.
7. If status checks are required, add:
   - `backend-format`
   - `frontend-lint`
   - `frontend-tests`
   - `frontend-build`
   - `backend-unit-tests`
   - `backend-tests`
   - `backend-coverage-gate`
   - `e2e-playwright`
8. Require branches to be up to date before merging when required checks are enabled.

Notes:
- This repository currently runs in a solo-maintainer context, so `required_approving_review_count` should stay at `0` on `main` and `develop`.
- `frontend-build` is now a first-class CI check and should remain required.
- `backend-tests` now enforces `>= 45%` total backend line coverage via `.coveragerc`. Treat this as the ratchet baseline and raise it gradually as coverage improves.
- `backend-coverage-gate` enforces `>= 70%` coverage on changed lines inside `backend/app/**` for pull requests, so new backend changes do not add fresh coverage debt.
- `e2e-playwright` is path-scoped: it runs only when `frontend/**` changes.
- `e2e-playwright` is additionally gated by the repository variable `RUN_E2E_PLAYWRIGHT`; leave it unset/`false` while the Playwright baseline is unstable, and flip it to `true` when the suite is stabilized.
- `deploy-staging` runs only on pushes to `develop` when `ENABLE_STAGING_DEPLOY=true` and the required staging variables/secrets are configured.
