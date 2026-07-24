## Why

The release flow can spend up to ten minutes in hand-written polling and can run the full CI suite multiple times for the same commit. Post-release hygiene also requires exact branch SHA equality, which creates a no-content synchronization PR even when `develop` is already fully represented by `main`.

## What Changes

- Treat `develop` and `main` as post-release aligned when their SHAs match or when `develop` is an ancestor of `main` and both refs have identical trees.
- Define a bounded, native CI-wait protocol for agents that forbids manual sleep loops and prevents merge fallthrough after timeout or failure.
- Run branch validation once on the pull-request event instead of duplicating the full suite on both temporary-branch push and pull request.
- Run Playwright independently from backend integration tests while preserving both as mandatory dependencies of `qa-gate`.
- Record validation evidence and before/after CI behavior without weakening PostgreSQL, OpenSpec, frontend, backend, or visual QA requirements.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `release-worktree-hygiene`: Define semantic post-release alignment and retain blocking behavior for real content divergence.
- `ci-testing-hardening`: Avoid duplicate temporary-branch runs, preserve the aggregate QA contract, and remove an unnecessary Playwright dependency from the success-path critical path.
- `agent-instruction-alignment`: Standardize bounded, single-owner CI waiting and safe manual merge behavior.

## Impact

- `scripts/release-guard`
- `.github/workflows/ci.yml`
- `AGENTS.md`
- Global `alan-workflow` skill and its operational guidance
- Release/QA evidence recorded on issue #326 and its pull request
