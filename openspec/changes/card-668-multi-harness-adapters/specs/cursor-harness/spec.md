## MODIFIED Requirements

### Requirement: Cursor is the versioned development harness
The repository SHALL contain a versioned Cursor **adapter** under `.cursor/` (rules, skills, commands, hooks) that compiles the process nucleus (`.cursor/process-fsm.yaml` + `scripts/process-fsm/` + root `AGENTS.md`). Cursor is not the only versioned client: Grok Build has a sibling adapter under `.grok/`. The repo MUST NOT keep OpenCode (`opencode.json`, `.opencode/`) as an active contract. `.cursor/rules/harness.mdc` SHALL identify the Cursor client (hooks + Task `inherit`) and MUST NOT repeat the δ table or the 12-column runbook.

#### Scenario: Fresh checkout loads Cursor config
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** project rules, OpenSpec skills/commands and the Impeccable hook are available from `.cursor/`
- **AND** no active instruction requires `.opencode/` or `opencode.json`

#### Scenario: No secrets in versioned harness files
- **WHEN** `.cursor/` is inspected
- **THEN** no token, key or credential is present in versioned files

#### Scenario: harness.mdc is Cursor identity not the law
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** the body names Cursor hooks and Task `inherit`
- **AND** it does not contain a T0–T17 table or `release-guard`

### Requirement: Column gate is always-on; full workflow is a skill
The always-on layer SHALL be the short root `AGENTS.md` plus the client paging (Cursor: `sessionStart` Moore page; Grok: generated `.grok/rules/` page). It MUST state that `Em Refinamento` is the entry column, Todo is not implementation, and Design columns must not be skipped. The detailed 12-column runbook SHALL live in the `alan-workflow` skill (on-demand). Chat requests such as `implemente` SHALL NOT authorize `/opsx:apply` or product code while `Status=Todo`. The always-on layer MUST NOT include the `AGENTS.md` overlay body (`docs/crypto-overlay.md`).

#### Scenario: Chat says implement all Todo cards
- **WHEN** the user asks to implement cards in `Status=Todo`
- **THEN** the agent SHALL start Design (OpenSpec + critique + Gist), not `/opsx:apply` or product code

#### Scenario: Todo session does not load release playbook
- **WHEN** a session starts bound to a card with `Status=Todo`
- **THEN** always-on context is `AGENTS.md` plus `context_file[Todo]`
- **AND** it MUST NOT include the release-guard closeout playbook

### Requirement: Root AGENTS.md is a stub; overlay is on-demand
The repository root `AGENTS.md` SHALL be a stub of at most 40 non-empty lines that points to `docs/crypto-overlay.md` for ports/URLs, Drive, PostgreSQL, and release-guard/lote/PROD, MUST include the board URL `github.com/users/oalansilva/projects/1`, and MUST carry the short always-on δ (resolve the tuple, chat ≠ δ, Todo ≠ código, Alan-only T1/T7/T15, clients Cursor and Grok Build). The long overlay body SHALL live in `docs/crypto-overlay.md` (not always-injected). Agents MUST `Read` that overlay only when the task needs those topics. The stub MUST NOT contain the 12-column runbook, `release-guard pre`/`post` snippets, or deploy PROD procedure.

#### Scenario: Fresh session does not ingest the overlay body from AGENTS.md
- **WHEN** the root `AGENTS.md` is read as the always-on workspace file
- **THEN** it has at most 40 non-empty lines
- **AND** it does not contain `scripts/release-guard pre` or the 12-column path as a procedure
- **AND** it names `docs/crypto-overlay.md` as the on-demand overlay
- **AND** it contains `github.com/users/oalansilva/projects/1`

#### Scenario: Stub names both clients and the tuple
- **WHEN** the root `AGENTS.md` is read
- **THEN** it mentions Cursor Agent and Grok Build
- **AND** it tells the agent to resolve `(q, bound_card, q_git)`
- **AND** it states that chat wording is not authorization

### Requirement: Always-on harness rule is 8-15 body lines
`.cursor/rules/harness.mdc` SHALL remain `alwaysApply: true`. Its body (non-empty lines after the YAML frontmatter) MUST contain between 4 and 12 lines. The body SHALL identify the Cursor client: hooks under `.cursor/hooks.json`, Task `inherit`, and that the always-on δ lives in `AGENTS.md`. It MUST NOT include the Code Review reviewer procedure, the OpenSpec Gist republication helper, the release closeout, a T0–T17 table, or a restatement of I1–I9.

#### Scenario: harness.mdc body budget
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** non-empty body lines are between 4 and 12 inclusive
- **AND** the body mentions Task `inherit` or Cursor hooks
- **AND** the body does not mention `diff-reviewer` or `release-guard`
- **AND** the body does not claim Grok Auto

### Requirement: Pronto closeout is process_event fechar_release
After an explicit release request, the Agent SHALL publish (`main`, deploy PROD, docs) using the overlay and `release-guard`. Closing Homologado → Pronto SHALL be `process_event fechar_release` with live `M_lote` (`release-guard post` PASS) for the `RELEASE_CARDS` package. The Agent MUST NOT treat `gh project item-edit` of Status or a chat `suba a release` / `autorizo Pronto` as T16. `priorizar`, `aprovar_design`, and `homologar` remain Alan-only. Always-on `AGENTS.md` SHALL say Alan-only is T1/T7/T15 (not T16). `.cursor/rules/harness.mdc` MUST NOT restate that table.

#### Scenario: Agent closes Homologado to Pronto after post PASS
- **WHEN** the package cards are Homologado, `release-guard post` exits 0, and the Agent runs `process_event fechar_release`
- **THEN** each package card moves to Pronto
- **AND** the Agent does not edit Project 1 Status via `gh project item-edit`

#### Scenario: Chat does not close Pronto
- **WHEN** the user says `implemente` or `autorizo Pronto` without `process_event fechar_release` succeeding
- **THEN** Status MUST remain Homologado

#### Scenario: Alan-only lives in AGENTS.md not harness.mdc
- **WHEN** `AGENTS.md` and `.cursor/rules/harness.mdc` are read
- **THEN** `AGENTS.md` states Alan-only T1/T7/T15
- **AND** `harness.mdc` does not contain the string `T1/T7/T15` as the always-on law
