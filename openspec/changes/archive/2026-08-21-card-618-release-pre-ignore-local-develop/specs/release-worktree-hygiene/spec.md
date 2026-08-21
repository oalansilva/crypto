## ADDED Requirements

### Requirement: Pre on release branch ignores unmerged local develop without PRESERVED_BRANCHES
When `scripts/release-guard` runs in `pre` mode and the current branch matches `release-*`, the Local branches inventory SHALL NOT emit the unmerged-local-branch blocker for the local ref `develop`, even when `refs/heads/develop` is not merged into `origin/develop` or `origin/main` (for example local develop ahead with unpublished commits). This exemption MUST NOT require `PRESERVED_BRANCHES` to include `develop`. The existing warning when local `develop` differs from `origin/develop` MAY remain. Other unmerged local branches MUST continue to block unless classified via `PRESERVED_BRANCHES` or otherwise already exempt. Modes `post` and `audit`, and `pre` when the current branch is not `release-*`, are unchanged by this requirement. The guard remains read-only.

#### Scenario: Pre on release-* with local develop ahead of origin/develop
- **WHEN** `pre` runs with current branch `release-*`
- **AND** local `develop` exists and is ahead of `origin/develop` (not `branch_merged`)
- **AND** `PRESERVED_BRANCHES` is unset or does not list `develop`
- **THEN** the guard MUST NOT emit `local branch not merged...: develop` (nor any BLOCKER solely for that local develop ref)
- **AND** the guard MUST NOT require `PRESERVED_BRANCHES=develop`

#### Scenario: Pre on release-* still blocks other unmerged local branches
- **WHEN** `pre` runs with current branch `release-*`
- **AND** a local branch other than `develop` (for example `card-999-wip`) is not merged into `origin/develop` or `origin/main`
- **AND** that branch is not listed in `PRESERVED_BRANCHES`
- **THEN** the guard emits the current unmerged-local-branch blocker for that branch

#### Scenario: Existing diverge warn for develop remains available
- **WHEN** `pre` runs with current branch `release-*`
- **AND** `refs/heads/develop` differs from `origin/develop`
- **THEN** the guard MAY warn that release decisions use `origin/develop`
- **AND** that diverge alone MUST NOT become a Local-branches BLOCKER for `develop` under this requirement
