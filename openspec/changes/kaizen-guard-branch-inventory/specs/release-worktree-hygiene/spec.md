# release-worktree-hygiene Specification

## Purpose
Release guard inventory e classificação obrigatória de branches `change-*/card-*/release-*` no closeout, incluindo deleção das branches do pacote após `Pronto`.

## MODIFIED Requirements

### Requirement: Post-release branch alignment MUST be semantic and safe
The release guard MUST accept post-release alignment when `origin/develop` and `origin/main` reference the same commit, or when `origin/develop` is an ancestor of `origin/main` and both refs have identical trees. It MUST reject histories with material content divergence or with integration history not represented by production. The guard SHALL additionally inventory orphan refs/worktrees in `post` mode and require classification before cleanup. The guard SHALL also inventory local and remote branches matching `change-*/card-*/release-*` in `post`/`audit` mode and require classification or deletion in closeout, including debt from previous releases.

#### Scenario: Remote refs have the same commit
- **WHEN** post-release validation compares identical `origin/develop` and `origin/main` commit IDs
- **THEN** the alignment check succeeds

#### Scenario: Main contains develop with an identical tree
- **WHEN** `origin/develop` is an ancestor of `origin/main`, their commit IDs differ, and their trees are identical
- **THEN** the alignment check succeeds without requiring a reverse synchronization PR

#### Scenario: Remote trees differ
- **WHEN** `origin/develop` and `origin/main` contain different file trees
- **THEN** strict post-release validation fails

#### Scenario: Develop is not represented by main
- **WHEN** `origin/develop` is not an ancestor of `origin/main` even though their trees are identical
- **THEN** strict post-release validation fails

#### Scenario: Change/card/release branches unclassified
- **WHEN** `post`/`audit` mode finds local or remote branches matching `change-*/card-*/release-*` that are not classified (integrated/preserved) or deleted
- **THEN** the guard reports them; in strict `post` mode the unclassified branches are blockers and the closeout checklist requires their deletion after cards reach `Pronto`

#### Scenario: Package branches deleted after Pronto
- **WHEN** the package cards are `Pronto` and the closeout checklist is executed
- **THEN** the package branches (`change-*`/`card-*`/`release-*`) are deleted locally and remotely, and the guard `post` no longer reports them
