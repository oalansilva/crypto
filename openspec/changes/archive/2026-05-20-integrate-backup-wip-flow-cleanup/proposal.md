## Why

A release found useful WIP mixed with Playwright debug output on `develop`, then preserved it on `backup/develop-wip-20260520-022324`. This change integrates the useful behavior and closes the workflow gap that let generated output look like releasable source.

## What Changes

- Integrate auth refresh resilience from the saved WIP so expired access tokens can recover without forcing logout or breaking Monitor chart flows.
- Integrate Monitor chart/favorite access fixes that are product behavior, while keeping generated debug artifacts out of Git history.
- Add ignore protection for operational output under `output/`.
- Document the root cause and expected release hygiene.

## Capabilities

### New Capabilities
- `release-worktree-hygiene`: Prevent generated release/debug output from being treated as releasable work and require classification before integration.

### Modified Capabilities
- `closed-beta-access-control`: Authenticated frontend requests recover from expired access tokens when a refresh token exists.
- `favorites`: Common users can read safe admin-catalog favorite details while private user favorites remain scoped.
- `monitor`: Monitor chart opening and timeframe behavior uses the validated operational defaults from the saved WIP.
- `chart-visualization`: Chart modals render above app chrome and keep localized user-facing labels.

## Impact

- Frontend auth store, authenticated fetch helper, Monitor cards/chart modal, chart data fetches and E2E tests.
- Backend favorites and opportunity service behavior.
- `.gitignore`, docs, OpenSpec specs, branch/release hygiene.
