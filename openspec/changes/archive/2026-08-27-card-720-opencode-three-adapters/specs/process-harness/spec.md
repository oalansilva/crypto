## MODIFIED Requirements

### Requirement: Process law has one nucleus and two adapters
The process SHALL have a single nucleus and three client adapters. The nucleus is `.cursor/process-fsm.yaml`, `scripts/process-fsm/`, the canonical skill files under `.cursor/skills/`, and the short root `AGENTS.md`. The Cursor adapter is `.cursor/hooks.json`, `.cursor/hooks/*`, `.cursor/rules/harness.mdc`, and `.cursor/commands/`. The Grok adapter is `.grok/hooks/`, generated Moore paging under `.grok/rules/`, and skill stubs under `.grok/skills/`. The OpenCode adapter is `.opencode/plugin/` (auto-loaded `*.js` / `*.ts`), Moore inject via `experimental.chat.system.transform`, and skill stubs under `.opencode/skills/` only for skills the OpenCode 1.18.18 binary does not discover. A change of column, invariant, product glob, or Moore `context_file` text MUST be made once in the yaml (and in a skill only when the change is *how* to work). Adapters MUST NOT copy T0–T17, I1–I9, or the 12-column runbook. Codex home skills and Hermes skill symlinks MUST NOT be an active contract. The lock machine (`design-planner` lease, packet, `design_artifact_write`, attestation, `opencode.db` as kaizen contract) MUST remain forbidden. `opencode.json` MUST NOT be an active contract of model, MCP, or permission.

#### Scenario: One yaml change reaches three adapters
- **WHEN** a glob, column, or `context_file` stub is changed in `.cursor/process-fsm.yaml`
- **THEN** the Cursor, Grok, and OpenCode Guard/paging paths compile from that yaml
- **AND** no second copy of the table exists in `.grok/rules/`, `.cursor/rules/`, or `.opencode/`

#### Scenario: Dual-write of the law is forbidden
- **WHEN** a reviewer inspects `.cursor/rules/`, `.grok/rules/`, and `.opencode/`
- **THEN** none of those directories contains a T0–T17 table, I1–I9 list, or 12-column procedure
- **AND** a Grok or OpenCode skill stub MUST NOT contain the runbook copied from `.cursor/skills/`

### Requirement: Always-on delta lives in AGENTS.md
The short always-on law (resolve `(q, bound_card, q_git)`, chat wording is not authorization, NLU is not δ, `Em Refinamento` is the entry column, `Todo` is not implementation, Design columns must not be skipped, overlay is on-demand, Alan-only T1/T7/T15, T16 is `process_event fechar_release`) SHALL live in the root `AGENTS.md` stub so Cursor, Grok Build, and OpenCode ingest it. `AGENTS.md` MUST remain at most 40 non-empty lines and MUST still point to `docs/crypto-overlay.md` for ports/Drive/PostgreSQL/release. It MUST name Cursor Agent, Grok Build, and OpenCode as clients. It MUST state that Cursor Auto is allowed and that Grok Build and OpenCode remain cooperative until their deny essays PASS. It MUST NOT claim Auto OpenCode or Auto Grok. It MUST NOT include the 12-column runbook or `release-guard pre`/`post` snippets. The file header MUST NOT say the stub is “não always-on” after this change.

#### Scenario: Three clients read the same always-on stub
- **WHEN** a Cursor session, a Grok session, and an OpenCode session start in the repo
- **THEN** all three load root `AGENTS.md`
- **AND** that file states that chat wording is not δ and that `Todo` is not implementation
- **AND** it states Alan-only T1/T7/T15
- **AND** it names Cursor Agent, Grok Build, and OpenCode
- **AND** it does not claim Grok Auto or OpenCode Auto is active
- **AND** it does not contain `scripts/release-guard pre`

## ADDED Requirements

### Requirement: OpenCode adapter is plugin skin not a second law
OpenCode 1.18.18 SHALL be an active client adapter. The versioned skin SHALL auto-load from `.opencode/plugin/` (singular; the 1.18.18 binary also discovers `.opencode/plugins/`, which MUST NOT be versioned). The repo MUST NOT add `opencode.json` (minimum or complete). The adapter MUST NOT add `.opencode/command/` or `.opencode/commands/` `/opsx-*` files; the OpenCode model uses the `skill` tool. Stubs under `.opencode/skills/<name>/SKILL.md` SHALL exist only for process skills the 1.18.18 binary does not discover (it discovers `.opencode/skills/` and `.agents/skills/`, not `.cursor/skills/`). Each stub MUST keep the canonical skill `name`, MUST instruct MUST Read of the canonical `SKILL.md`, MUST keep body (non-empty lines after frontmatter) at most 8 lines, and MUST NOT copy T0–T17. Impeccable (skill) already lives in `.agents/skills/impeccable/` and MUST NOT be duplicated as a second runbook.

#### Scenario: Plugin auto-loads without opencode.json
- **WHEN** OpenCode 1.18.18 starts in the repo with no `opencode.json`
- **THEN** `*.js` or `*.ts` under `.opencode/plugin/` load
- **AND** no `opencode.json` is present
- **AND** `.opencode/plugins/` is not versioned as a second copy

#### Scenario: No opsx commands in OpenCode
- **WHEN** a reviewer lists `.opencode/command/` and `.opencode/commands/`
- **THEN** there is no `opsx-*` command file

#### Scenario: OpenCode stub is a bridge
- **WHEN** an OpenCode session needs `alan-workflow`
- **THEN** `.opencode/skills/alan-workflow/SKILL.md` exists
- **AND** its body tells the agent to Read `.cursor/skills/alan-workflow/SKILL.md`
- **AND** the stub body does not contain the 12-column path as a procedure

### Requirement: Impeccable detector is on all three clients
The Impeccable **detector** SHALL be the same `.agents/skills/impeccable/scripts/hook.mjs` on Cursor, Grok Build, and OpenCode. Adapters SHALL only translate native events. Cursor remains `.cursor/hooks.json` `afterFileEdit` / `stop` via `.cursor/hooks/impeccable.sh`. Grok SHALL register `PostToolUse` and `Stop` under `.grok/hooks/` mapping to that `hook.mjs` (`afterFileEdit` Cursor maps to `PostToolUse`). OpenCode SHALL register `tool.execute.after` and `session.idle` in the 1.18.18 plugin mapping to the same `hook.mjs`. The detector MUST be fail-open: a finding or a crash of `hook.mjs` MUST NOT abort the turn. This requirement MUST NOT introduce a second detector, MUST NOT restore the lock machine, and MUST NOT reopen #668 Guard/paging.

#### Scenario: UI edit on any client runs hook.mjs
- **WHEN** a UI file (`frontend/src/**` or equivalent screen file) is edited in Cursor, Grok, or OpenCode 1.18.18
- **THEN** the same `hook.mjs` runs
- **AND** a detector finding does not abort the turn

#### Scenario: Grok registers PostToolUse and Stop
- **WHEN** `.grok/hooks/` is loaded in a trusted folder
- **THEN** `PostToolUse` and `Stop` invoke the Impeccable adapter that calls `hook.mjs`

#### Scenario: OpenCode registers after and idle
- **WHEN** the OpenCode plugin loads
- **THEN** `tool.execute.after` and `session.idle` invoke the Impeccable adapter that calls `hook.mjs`

#### Scenario: OpenCode after maps filePath to hook.mjs
- **WHEN** `tool.execute.after` fires with `args.filePath` of a UI file
- **THEN** `hook.mjs` stdin has `file_path` set from that `filePath` and `hook_event_name` equal to `PostToolUse`
- **AND** the turn is not aborted

#### Scenario: OpenCode idle maps to Stop
- **WHEN** `session.idle` fires
- **THEN** `hook.mjs` stdin has `hook_event_name` equal to `Stop`
- **AND** the turn is not aborted

### Requirement: OpenCode Auto is gated on the deny essay
Until a human essay on the same worktree shows that an illegal product Write with `q_git=develop` is denied in the OpenCode 1.18.18 session (plugin loaded), OpenCode MUST be treated as cooperative, not Auto. Grok Build remains cooperative until the #668 4.5 essay PASS. This card MUST NOT inherit Cursor Auto. `process_event` remains the only Agent Status mover in all three clients. Agent MUST NOT `item-edit` Status. OpenCode `bash` that performs Status `item-edit` MUST be denied by the same Guard.

#### Scenario: Essay not yet green
- **WHEN** the OpenCode deny essay has not been recorded as PASS
- **THEN** docs and always-on text MUST NOT claim OpenCode Auto is active
- **AND** the compiled Guard for OpenCode MUST still deny illegal product writes (the gate is operational claim, not an excuse to skip the adapter)

#### Scenario: process_event is the Status mover in three clients
- **WHEN** a Grok, Cursor, or OpenCode agent needs to move Project 1 Status
- **THEN** it SHALL call `scripts/process-fsm/process_event.py` with a named event
- **AND** it MUST NOT `gh project item-edit` the Status field
