## ADDED Requirements

### Requirement: Post-release branch alignment MUST be semantic and safe
The release guard MUST accept post-release alignment when `origin/develop` and `origin/main` reference the same commit, or when `origin/develop` is an ancestor of `origin/main` and both refs have identical trees. It MUST reject histories with material content divergence or with integration history not represented by production.

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
