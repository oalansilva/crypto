## Context

The current release closeout compares `origin/develop` and `origin/main` by commit ID. A normal merge to `main` creates a different commit even when both refs contain the same files, so the strict post-release guard forces a reverse synchronization PR. The CI workflow then runs the same full suite for the temporary branch push and the pull request, while Playwright waits for backend integration tests despite sharing no artifacts with that job.

Agent guidance requires terminal CI evidence but does not define how to wait. Agents therefore may invent foreground polling loops that repeatedly query mergeability, sleep, and fall through to a merge attempt after the loop expires.

Constraints:

- `qa-gate`, PostgreSQL tests, OpenSpec validation, frontend checks, and visual Playwright remain mandatory.
- Push and pull-request concurrency groups must remain separated by `github.event_name`.
- Release merge remains manual; this change does not authorize auto-merge.
- A real content difference between `develop` and `main` must still block post-release closeout.

## Goals / Non-Goals

**Goals:**

- Eliminate reverse synchronization PRs that contain no material change.
- Avoid duplicate full CI runs for temporary branches with pull requests.
- Shorten the successful CI critical path by running independent jobs concurrently.
- Give agents one bounded, native, single-owner protocol for waiting on required checks.
- Preserve all existing QA and release safety guarantees.

**Non-Goals:**

- Skip visual QA based on paths or implicit repository settings.
- Change branch protection or required-check policy.
- Introduce auto-merge.
- Parallelize backend unit tests before PostgreSQL isolation and timing evidence exist.
- Archive this OpenSpec change before Alan homologates the card and requests a release.

## Decisions

### Decision: Use ancestry plus tree equality for semantic alignment

`release-guard post` will pass when the remote commit IDs match. When they differ, it will also pass only if `origin/develop` is an ancestor of `origin/main` and both commit trees are identical. This proves that production contains the integration history and that neither branch has a material file difference.

Commit equality alone was rejected because merge commits create harmless SHA differences. Tree equality alone was rejected because it would accept unrelated histories or a `develop` commit not represented in production.

### Decision: Validate temporary branches on pull-request events

The workflow will run on pushes to `develop` and `main`, and on pull requests targeting those branches. A temporary branch no longer launches the full suite once on push and again when its PR opens. Integration and production pushes retain their own validation runs.

Using one concurrency group across push and pull-request events was rejected because one event could cancel the other and leave a required check cancelled.

### Decision: Run Playwright independently of backend integration tests

`e2e-playwright` will depend on the pull-request policy job but not on `backend-tests`. The jobs use separate runners and share no build or coverage artifact, so the dependency only serializes the success path. `qa-gate` will continue to require successful results from both jobs.

Path-based Playwright skipping was rejected because visual QA is mandatory for every card.

### Decision: Standardize native bounded CI watching

Agent instructions will forbid hand-written `for`/`while` plus `sleep` loops. One owner will use `gh pr checks <PR> --watch --fail-fast --interval 20` with an explicit timeout. The watcher will include all reported checks, not only branch-protection-required contexts, because every started check must finish and OpenSpec may not be configured as required on every target branch. When background execution is available and expected wait exceeds 60 seconds, the watcher will run in the background so the agent can perform independent closeout work.

Timeout, watcher failure, or a non-clean merge state will stop the merge phase. The agent will query mergeability once after checks succeed and perform at most one manual merge attempt for that observed clean state. A failed attempt requires diagnosis and a fresh complete readiness check before any retry.

## Risks / Trade-offs

- [Temporary branch pushes no longer run hosted CI before a PR exists] → Keep focused local validation before Code Review and open the PR immediately after the reviewed SHA is pushed to enter QA.
- [Tree equality could hide a missing merge-only metadata commit] → Require `develop` ancestry in addition to tree equality; any material metadata file difference still blocks.
- [Parallel Playwright consumes runner capacity even if backend tests later fail] → Accept limited extra failure-path cost in exchange for a shorter successful critical path; `qa-gate` remains authoritative.
- [A foreground native watcher still displays waiting] → Require background execution when supported and avoid LLM-driven polling turns.
- [Global skill source may live outside the application repository] → Update the canonical skill source under its own repository rules and record separate preservation evidence if needed.

## Migration Plan

1. Add focused tests for post-release alignment cases.
2. Update `release-guard`, CI triggers, and Playwright dependencies.
3. Update project and global agent instructions.
4. Validate shell behavior, workflow syntax, OpenSpec, and the exact diff.
5. Push the reviewed SHA and observe one pull-request suite.
6. Keep the OpenSpec change active through Done/Homologado; archive only in a later release.

Rollback consists of reverting the application-repository commit and the corresponding global-skill commit. Existing branch protection remains unchanged throughout.

## Open Questions

None. Backend test sharding remains a separately measured follow-up if the critical path is still above target after these changes.
