## MODIFIED Requirements

### Requirement: Cursor is the versioned development harness
The repository SHALL contain a versioned Cursor **adapter** under `.cursor/` (rules, skills, commands, hooks) that compiles the process nucleus (`.cursor/process-fsm.yaml` + `scripts/process-fsm/` + root `AGENTS.md`). Cursor is not the only versioned client: Grok Build has a sibling adapter under `.grok/`, OpenCode 1.18.18 has a sibling adapter under `.opencode/plugin/` (auto-load; no `opencode.json`), and dsh has a sibling adapter under `.dsh/plugin/` (Cordis native; no Claude `hooks.json` Guard). The repo MUST NOT restore the lock machine (`design_spawn_stage`, `design_artifact_write`, lease, packet, attestation, `opencode.db` as kaizen contract). `opencode.json` MUST NOT be an active contract of model, MCP, or permission. `.cursor/rules/harness.mdc` SHALL identify the Cursor client (hooks + Task `inherit`) and MUST NOT repeat the δ table or the 12-column runbook. The fourth harness (dsh) MUST NOT be a source of law.

#### Scenario: Fresh checkout loads Cursor config
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** project rules, OpenSpec skills/commands and the Impeccable hook are available from `.cursor/`
- **AND** no Cursor instruction requires `opencode.json` as a model/MCP/permission contract

#### Scenario: No secrets in versioned harness files
- **WHEN** `.cursor/` is inspected
- **THEN** no token, key or credential is present in versioned files

#### Scenario: harness.mdc is Cursor identity not the law
- **WHEN** `.cursor/rules/harness.mdc` is counted excluding the YAML frontmatter
- **THEN** the body names Cursor hooks and Task `inherit`
- **AND** it does not contain a T0–T17 table or `release-guard`

### Requirement: Root AGENTS.md is a stub; overlay is on-demand
The repository root `AGENTS.md` SHALL be a stub of at most 40 non-empty lines that points to the consumer `overlay_doc` (Cripto: `docs/crypto-overlay.md`) for ports/URLs, Drive, PostgreSQL, and release-guard/lote/PROD, MUST include the board URL generated from overlay `board.owner` and `board.number` (Cripto: `github.com/users/oalansilva/projects/1`), and MUST carry the short always-on δ (resolve the tuple, chat ≠ δ, Todo ≠ código, Alan-only T1/T7/T15, clients Cursor, Grok Build, OpenCode, and dsh). The long overlay body SHALL live at `overlay_doc` (not always-injected). Agents MUST `Read` that overlay only when the task needs those topics. The stub MUST NOT contain the 12-column runbook, `release-guard pre`/`post` snippets, or deploy PROD procedure. The stub MUST NOT claim Auto OpenCode, Auto Grok, or Auto dsh. `render_agents()` MUST emit those four names even when overlay omits `clients.dsh`.

#### Scenario: Fresh session does not ingest the overlay body from AGENTS.md
- **WHEN** the root `AGENTS.md` is read as the always-on workspace file
- **THEN** it has at most 40 non-empty lines
- **AND** it does not contain `scripts/release-guard pre` or the 12-column path as a procedure
- **AND** it names the consumer `overlay_doc` as the on-demand overlay
- **AND** it contains a board URL derived from overlay board fields (Cripto: `github.com/users/oalansilva/projects/1`)

#### Scenario: Stub names four clients and the tuple
- **WHEN** the root `AGENTS.md` is read
- **THEN** it mentions Cursor Agent, Grok Build, OpenCode, and dsh
- **AND** it tells the agent to resolve `(q, bound_card, q_git)`
- **AND** it states that chat wording is not authorization
- **AND** it does not claim OpenCode Auto, Grok Auto, or dsh Auto
