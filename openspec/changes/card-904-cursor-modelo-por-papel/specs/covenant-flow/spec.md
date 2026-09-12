## ADDED Requirements

### Requirement: Cursor Task model follows role not picker
The canonical Cursor runbook `.cursor/skills/covenant-flow/SKILL.md` SHALL stop telling every Task/subagent to inherit the parent picker. It SHALL state that the law is the Task `model` parameter on both spawn paths. Juízo (grelha, Design-autor, crítico, Assessment A/B) SHALL be Grok 4.6 (`cursor-grok-4.6-high`). Execução (Apply, QA, the two reviewers, same-card explore, fecho-lote) SHALL be Composer 2.5 (`composer-2.5`). `composer-2.5-fast` MUST NOT be listed as a happy path. Reviewers on Grok MUST NOT be listed as a happy path of this change. Always-on `AGENTS.md` MUST NOT grow with the table. Isolation of existing children (no parent transcript, destape needles, sidecar, Q2–Q6, review ceiling 1+1) SHALL remain as already specified.

#### Scenario: Runbook names role models not inherit
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` is read
- **THEN** it tells the parent to pass Task `model` per role
- **AND** it MUST NOT say that isolated children inherit the picker
- **AND** `AGENTS.md` does not contain the role table

### Requirement: Other-client stubs keep inherit without copying the table
Grok Build, OpenCode, and dsh skill stubs SHALL continue to map children to inherit. Each stub body (non-empty lines after frontmatter) MUST stay at most 8 lines and MUST NOT copy the Cursor role table. This change MUST NOT dual-write law into `.grok/`, `.opencode/`, or `.dsh/`.

#### Scenario: Grok stub stays a short inherit bridge
- **WHEN** `.grok/skills/covenant-flow/SKILL.md` is counted excluding frontmatter
- **THEN** non-empty body lines are at most 8
- **AND** it still maps Cursor Task inherit to `spawn_subagent` inherit
- **AND** it does not list Grok 4.6 versus Composer 2.5 by role

## MODIFIED Requirements

### Requirement: Review stance lives in local reviewers not BUGBOT.md
The product SHALL version `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md` with `model: composer-2.5` and `readonly`. Review constraints SHALL live in those files. `REVIEW.md` MAY exist in a consumer and MUST NOT mention Bugbot. The product MUST NOT ship `.cursor/BUGBOT.md` or nested homonyms and MUST NOT use Cursor Bugbot (`/review-bugbot`) as Code Review. Code Review gate SHALL be `diff-reviewer` plus `code-reviewer`. `/review-security` MAY run when Alan explicitly asks. The YAML `model` is a redundant pin; Cursor Code Review spawns SHALL pass `model: composer-2.5` on both spawn paths.

#### Scenario: Product has no BUGBOT.md
- **WHEN** the product tree and a uniquely pinned Cripto tree are listed
- **THEN** no `BUGBOT.md` exists (root or nested)
- **AND** `diff-reviewer.md` and `code-reviewer.md` exist with `readonly: true` and `model: composer-2.5`

#### Scenario: Optional REVIEW.md has no Bugbot
- **WHEN** a consumer adds `REVIEW.md`
- **THEN** that file does not mention Bugbot
- **AND** Code Review gate remains the two local reviewers
- **AND** `/review-security` MAY run only when Alan explicitly asks
