## MODIFIED Requirements

### Requirement: Versioned local reviewer subagents exist
The repository SHALL contain `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`, each with `readonly: true` and `model: composer-2.5`. The YAML `model` is a redundant pin; the law is the Task `model` parameter of the spawn. Neither file SHALL declare `model: inherit`.

#### Scenario: Reviewer files are versioned
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** both agent files are available for delegation during Code Review
- **AND** each MUST declare `readonly: true` and `model: composer-2.5`
- **AND** neither MUST declare `model: inherit`

### Requirement: Review stance lives in local reviewer agents
The repository SHALL contain `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`, each with `readonly: true` and `model: composer-2.5`, and those files SHALL carry review constraints (Design/`Pronto para Dev` not skippable, no secrets in commits, consumer overlay `runtime.database` when present, tests when backend changes, Playwright visual when UI changes). `REVIEW.md` MAY exist and MUST NOT mention Bugbot. `BUGBOT.md` MUST NOT exist. Cursor Bugbot MUST NOT be the Code Review path.

#### Scenario: Reviewer files carry the stance
- **WHEN** a local `diff-reviewer` run starts
- **THEN** `.cursor/agents/diff-reviewer.md` exists and encodes the review constraints
- **AND** `.cursor/BUGBOT.md` does not exist

#### Scenario: Nested BUGBOT.md is gone
- **WHEN** the reviewed diff includes `backend/` or `frontend/` files
- **THEN** no nested `BUGBOT.md` is required
- **AND** the same agent files apply
