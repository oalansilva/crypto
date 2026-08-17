## ADDED Requirements

### Requirement: Versioned review rules exist in the repo
The repository SHALL contain `.cursor/BUGBOT.md` at the project root and nested `backend/.cursor/BUGBOT.md` and `frontend/.cursor/BUGBOT.md`. Local reviewers SHALL read these files. Cursor project rules (`*.mdc`) MUST NOT be treated as a substitute.

#### Scenario: Root BUGBOT.md is present
- **WHEN** a local `diff-reviewer` run starts
- **THEN** `.cursor/BUGBOT.md` exists and encodes Cripto review constraints (PostgreSQL required, no SQLite, Design/`Pronto para Dev` not skippable, no secrets in commits, tests when `backend/**` changes, Playwright visual when UI changes)

#### Scenario: Nested rules apply by tree
- **WHEN** the reviewed diff includes `backend/` files
- **THEN** `backend/.cursor/BUGBOT.md` is available for that review
- **WHEN** the reviewed diff includes `frontend/` files
- **THEN** `frontend/.cursor/BUGBOT.md` is available for that review

### Requirement: Versioned local reviewer subagents exist
The repository SHALL contain `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`, each with `readonly: true` and `model: inherit`.

#### Scenario: Reviewer files are versioned
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** both agent files are available for delegation during Code Review
- **AND** each MUST declare `readonly: true` and `model: inherit`
