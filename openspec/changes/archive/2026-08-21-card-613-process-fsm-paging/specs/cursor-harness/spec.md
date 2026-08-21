## ADDED Requirements

### Requirement: Root AGENTS.md is a stub; overlay is on-demand
The repository root `AGENTS.md` SHALL be a stub of at most 40 non-empty lines that points to `docs/crypto-overlay.md` for ports/URLs, Drive, PostgreSQL, and release-guard/lote/PROD, and MUST include the board URL `github.com/users/oalansilva/projects/1`. The long overlay body SHALL live in `docs/crypto-overlay.md` (not always-injected by Cursor). Agents MUST `Read` that overlay only when the task needs those topics. The stub MUST NOT contain the 12-column runbook, `release-guard pre`/`post` snippets, or deploy PROD procedure.

#### Scenario: Fresh session does not ingest the overlay body from AGENTS.md
- **WHEN** the root `AGENTS.md` is read as the always-on workspace file
- **THEN** it has at most 40 non-empty lines
- **AND** it does not contain `scripts/release-guard pre` or the 12-column path as a procedure
- **AND** it names `docs/crypto-overlay.md` as the on-demand overlay
- **AND** it contains `github.com/users/oalansilva/projects/1`

### Requirement: Always-on harness rule is 8-15 body lines
`.cursor/rules/harness.mdc` SHALL remain `alwaysApply: true` and its body (non-empty lines after the YAML frontmatter) MUST contain between 8 and 15 lines. The body SHALL tell the agent to resolve `(q, bound_card, q_git)`, that chat wording is not authorization, that NLU is not δ, that `Todo` is not implementation, and that the overlay is on-demand. It MUST NOT include the Code Review reviewer procedure, the OpenSpec Gist republication helper, or the release closeout.

#### Scenario: harness.mdc body budget
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** non-empty body lines are between 8 and 15 inclusive
- **AND** the body mentions resolving `(q, bound_card, q_git)`
- **AND** the body does not mention `diff-reviewer` or `release-guard`

### Requirement: alan-workflow skill priority is delta and Guard first
`.cursor/skills/alan-workflow/SKILL.md` SHALL declare priority order **δ and Guard > overlay > skill > wording**. Chat utterances such as `implemente` MUST be classified as wording (lowest). Overlay (`docs/crypto-overlay.md`) MUST be loaded only when ports, Drive, PostgreSQL, or release are in scope.

#### Scenario: Skill lists inverted priority
- **WHEN** `.cursor/skills/alan-workflow/SKILL.md` is opened
- **THEN** the priority list places δ/Guard before overlay, overlay before the skill runbook, and wording last
- **AND** it no longer lists “Instrução direta de Alan no chat” as item 1 ahead of δ

## MODIFIED Requirements

### Requirement: Column gate is always-on; full workflow is a skill
The always-apply harness rule SHALL state that `Em Refinamento` is the entry column, Todo is not implementation, and Design columns must not be skipped. The detailed 12-column runbook SHALL live in the `alan-workflow` skill (on-demand). Chat requests such as `implemente` SHALL NOT authorize `/opsx:apply` or product code while `Status=Todo`. The always-on layer SHALL be the short `harness.mdc` plus the `sessionStart` Moore page; it MUST NOT include the `AGENTS.md` overlay body.

#### Scenario: Chat says implement all Todo cards
- **WHEN** the user asks to implement cards in `Status=Todo`
- **THEN** the agent SHALL start Design (OpenSpec + critique + Gist), not `/opsx:apply` or product code

#### Scenario: Todo session does not load release playbook
- **WHEN** a session starts bound to a card with `Status=Todo`
- **THEN** always-on context is harness.mdc plus `context_file[Todo]`
- **AND** it MUST NOT include the release-guard closeout playbook
