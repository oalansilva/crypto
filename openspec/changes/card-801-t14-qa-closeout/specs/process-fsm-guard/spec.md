## ADDED Requirements

### Requirement: Guard denies card-branch checkout on the canonical DEV source
The Guard `beforeShellExecution` path (and the bash fallback) SHALL classify, **before** the missing-path early-return, a command that creates a `card-*` branch on overlay `environments.dev.source`. It MUST deny `git checkout -b card-*`, `git checkout --track -b card-*`, and `git switch -c card-*` when `cwd` or `git -C` resolves to that source path. The deny `reason` SHALL be `canonical_card_branch`. The same command in a worktree that is not the canonical source MUST NOT be denied by this rule. `git checkout` of an existing branch, `git worktree add`, and `git status` MUST NOT be denied by this rule. The packaged Guard MUST read the source path from overlay `environments.dev.source`, not a hardcoded string in the requirement tests' production module as the only source of truth. Unit tests MUST inject overlay/cwd/command and MUST NOT call GitHub.

#### Scenario: checkout -b card-* on canonical source is denied
- **WHEN** `beforeShellExecution` stdin `command` is `git checkout -b card-801-t14-qa-closeout` and `cwd` is overlay `environments.dev.source`
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` names reason `canonical_card_branch`

#### Scenario: switch -c card-* on canonical source is denied
- **WHEN** `beforeShellExecution` stdin `command` is `git switch -c card-792-x` and `cwd` is overlay `environments.dev.source`
- **THEN** the Guard returns `permission: deny`

#### Scenario: checkout -b card-* in a card worktree is not denied by this rule
- **WHEN** `beforeShellExecution` stdin `command` is `git checkout -b card-801-t14-qa-closeout` and `cwd` is a worktree path that is not `environments.dev.source`
- **THEN** this rule MUST NOT return `permission: deny`

#### Scenario: checkout of an existing branch on canonical source is not denied by this rule
- **WHEN** `beforeShellExecution` stdin `command` is `git checkout develop` and `cwd` is overlay `environments.dev.source`
- **THEN** this rule MUST NOT return `permission: deny`
