## MODIFIED Requirements

### Requirement: Cursor is the versioned development harness
The repository SHALL contain a versioned Cursor **adapter** under `.cursor/` (rules, skills, commands, hooks) that compiles the process nucleus (`.cursor/process-fsm.yaml` + `scripts/process-fsm/` + root `AGENTS.md`). Cursor is not the only versioned client: Grok Build has a sibling adapter under `.grok/`, and OpenCode 1.18.18 has a sibling adapter under `.opencode/plugin/` (auto-load; no `opencode.json`). The repo MUST NOT restore the lock machine (`design_spawn_stage`, `design_artifact_write`, lease, packet, attestation, `opencode.db` as kaizen contract). `opencode.json` MUST NOT be an active contract of model, MCP, or permission. `.cursor/rules/harness.mdc` SHALL identify the Cursor client (hooks + Task `inherit`) and MUST NOT repeat the δ table or the 12-column runbook.

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
The repository root `AGENTS.md` SHALL be a stub of at most 40 non-empty lines that points to `docs/crypto-overlay.md` for ports/URLs, Drive, PostgreSQL, and release-guard/lote/PROD, MUST include the board URL `github.com/users/oalansilva/projects/1`, and MUST carry the short always-on δ (resolve the tuple, chat ≠ δ, Todo ≠ código, Alan-only T1/T7/T15, clients Cursor, Grok Build, and OpenCode). The long overlay body SHALL live in `docs/crypto-overlay.md` (not always-injected). Agents MUST `Read` that overlay only when the task needs those topics. The stub MUST NOT contain the 12-column runbook, `release-guard pre`/`post` snippets, or deploy PROD procedure. The stub MUST NOT claim Auto OpenCode or Auto Grok.

#### Scenario: Fresh session does not ingest the overlay body from AGENTS.md
- **WHEN** the root `AGENTS.md` is read as the always-on workspace file
- **THEN** it has at most 40 non-empty lines
- **AND** it does not contain `scripts/release-guard pre` or the 12-column path as a procedure
- **AND** it names `docs/crypto-overlay.md` as the on-demand overlay
- **AND** it contains `github.com/users/oalansilva/projects/1`

#### Scenario: Stub names three clients and the tuple
- **WHEN** the root `AGENTS.md` is read
- **THEN** it mentions Cursor Agent, Grok Build, and OpenCode
- **AND** it tells the agent to resolve `(q, bound_card, q_git)`
- **AND** it states that chat wording is not authorization
- **AND** it does not claim OpenCode Auto or Grok Auto

## ADDED Requirements

### Requirement: OpenCode lock machine stays dead
While OpenCode 1.18.18 is an active adapter, Design and Apply flows MUST NOT require `design_spawn_stage`, `design_artifact_write`, lease evidence, packet, or OpenCode 1.18.18 attestation. Decision-log for this change SHALL revoke only the #562 uniqueness of Cursor as the sole operational harness; it MUST NOT revoke the death of the lock machine.

#### Scenario: Design in OpenCode does not require lease
- **WHEN** Design runs in OpenCode 1.18.18
- **THEN** the flow MUST NOT require `design_spawn_stage`, `design_artifact_write`, lease evidence, or attestation
