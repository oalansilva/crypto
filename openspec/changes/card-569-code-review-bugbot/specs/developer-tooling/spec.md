## ADDED Requirements

### Requirement: Versioned Bugbot rules exist in the repo
The repository SHALL contain `.cursor/BUGBOT.md` at the project root and nested `backend/.cursor/BUGBOT.md` and `frontend/.cursor/BUGBOT.md`. Cursor project rules (`*.mdc`) MUST NOT be treated as Bugbot review rules.

#### Scenario: Root BUGBOT.md is present
- **WHEN** a Bugbot or `/review-bugbot` run starts
- **THEN** `.cursor/BUGBOT.md` exists and encodes Cripto review constraints (PostgreSQL required, no SQLite, Design/`Pronto para Dev` not skippable, no secrets in commits, tests when `backend/**` changes, Playwright visual when UI changes)

#### Scenario: Nested rules apply by tree
- **WHEN** the reviewed diff includes `backend/` files
- **THEN** `backend/.cursor/BUGBOT.md` is available for that review
- **WHEN** the reviewed diff includes `frontend/` files
- **THEN** `frontend/.cursor/BUGBOT.md` is available for that review

### Requirement: Versioned process reviewer subagent exists
The repository SHALL contain `.cursor/agents/code-reviewer.md` with `readonly: true` and `model: inherit`, focused on process/contract review.

#### Scenario: Process reviewer file is versioned
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** `.cursor/agents/code-reviewer.md` is available for delegation during Code Review
- **AND** it MUST declare `readonly: true` and `model: inherit`
