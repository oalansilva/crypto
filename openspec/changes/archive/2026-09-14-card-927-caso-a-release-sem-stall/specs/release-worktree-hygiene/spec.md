## ADDED Requirements

### Requirement: Caso A preflight refuses an incomplete package before the PR
When `scripts/release-guard pre` runs on a current branch matching `release-*` and the unpublished diff is a code PR, the guard or the Caso A runbook MUST fail closed if a local frontend compile fails because a module born outside the package is absent. The operator MUST NOT open the lote PR. The compile MUST NOT write tracked `frontend/dist` as a guard side effect. The guard remains read-only with respect to git refs. This requirement MUST NOT close lote #916/#917.

#### Scenario: Missing module from a card outside the package
- **WHEN** `pre` runs on `release-*` whose tip omits a frontend module born on another card outside the lote
- **AND** local frontend compile fails
- **THEN** the command exits non-zero
- **AND** the runbook MUST NOT proceed to `gh pr create`

#### Scenario: Complete package compile passes this gate
- **WHEN** `pre` runs on `release-*` and local frontend compile succeeds
- **THEN** this gate does not block
- **AND** other existing `pre` blockers still apply

### Requirement: Post requires each package card to have a commit in production
In `post`, when `RELEASE_CARDS` is a non-empty canonical list, each id MUST have at least one commit reachable from `origin/main` that references that card (`#<id>` as a word in subject or body). Absence for any package id MUST be a blocker. This check MUST NOT close lote #916/#917.

#### Scenario: Package card missing from origin/main
- **WHEN** `post` runs with `RELEASE_CARDS` including N
- **AND** no commit reachable from `origin/main` references `#N`
- **THEN** the guard blocks

#### Scenario: Every package card is on origin/main
- **WHEN** each canonical id has a referencing commit on `origin/main`
- **THEN** this gate passes

## MODIFIED Requirements

### Requirement: Post-release branch alignment MUST be semantic and safe
The release guard MUST accept post-release alignment when `origin/develop` and `origin/main` reference the same commit, or when `origin/main` is an ancestor of `origin/develop` (produção contida na develop). Extra commits or files on `origin/develop` that are not in `origin/main` SHALL be inventoried as a warning and MUST NOT block. The guard MUST reject when `origin/main` is not an ancestor of `origin/develop`. Identical trees MUST NOT be required. `origin/develop` being an ancestor of `origin/main` MUST NOT be required. The guard SHALL additionally inventory orphan refs/worktrees in `post` mode and require classification before cleanup.

#### Scenario: Remote refs have the same commit
- **WHEN** post-release validation compares identical `origin/develop` and `origin/main` commit IDs
- **THEN** the alignment check succeeds

#### Scenario: Develop contains production with extra on develop
- **WHEN** `origin/main` is an ancestor of `origin/develop`, their commit IDs differ, and `origin/develop` has extra commits or a different tree
- **THEN** the alignment check succeeds
- **AND** the extra on develop is reported as a warning
- **AND** identical trees MUST NOT be required

#### Scenario: Develop does not contain production
- **WHEN** `origin/main` is not an ancestor of `origin/develop` and the commits differ
- **THEN** strict post-release validation fails

#### Scenario: Identical trees without production contained in develop still fail
- **WHEN** trees are identical but `origin/main` is not an ancestor of `origin/develop` and the commits differ
- **THEN** strict post-release validation fails
