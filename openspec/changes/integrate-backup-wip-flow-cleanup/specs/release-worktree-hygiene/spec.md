## ADDED Requirements

### Requirement: Generated output excluded from release integration
The repository SHALL ignore root-level generated operational output so debug artifacts are not treated as releasable source files.

#### Scenario: Playwright debug output exists locally
- **WHEN** a local run creates files under `output/playwright`
- **THEN** `git status --short` does not report those files as untracked release work

### Requirement: Preserved WIP is classified before release cleanup
The release workflow MUST classify saved WIP as integrated, intentionally excluded, or still preserved before removing backup branches or worktrees.

#### Scenario: Backup branch contains source and debug artifacts
- **WHEN** a saved backup branch is reviewed after release
- **THEN** useful source changes are integrated through a normal branch and debug artifacts are excluded from `develop` and `main`
