# Branch protection (`main` and `develop`)

Recommended GitHub settings for `main` and `develop`:

1. Require a pull request before merging.
2. Require at least 1 approval before merging.
3. Require conversation resolution before merging.
4. Dismiss stale approvals when new commits are pushed.
5. Restrict direct pushes to protected branches.
6. Optionally require status checks to pass before merging.
7. If status checks are required, add:
   - `backend-format`
   - `frontend-lint`
   - `backend-tests`
   - `e2e-playwright`
8. Require branches to be up to date before merging when required checks are enabled.

Notes:
- `RUN_FRONTEND_BUILD` is currently `false` in CI because `npm run build` fails on a known TypeScript error in `frontend/src/pages/ArbitragePage.tsx`.
- When frontend build is green, set `RUN_FRONTEND_BUILD` to `true` and include that check in required status checks.
- `e2e-playwright` is path-scoped: it runs only when `frontend/**` changes.
- `e2e-playwright` is additionally gated by the repository variable `RUN_E2E_PLAYWRIGHT`; leave it unset/`false` while the Playwright baseline is unstable, and flip it to `true` when the suite is stabilized.
