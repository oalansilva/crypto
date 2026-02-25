# Branch protection (main)

Recommended GitHub settings for `main`:

1. Require a pull request before merging.
2. Require status checks to pass before merging.
3. Add required checks:
   - `backend-tests`
   - `e2e-playwright`
4. Require branches to be up to date before merging.
5. Restrict direct pushes to `main`.

Notes:
- `RUN_FRONTEND_BUILD` is currently `false` in CI because `npm run build` fails on a known TypeScript error in `frontend/src/pages/ArbitragePage.tsx`.
- When frontend build is green, set `RUN_FRONTEND_BUILD` to `true` and include that check in required status checks.
