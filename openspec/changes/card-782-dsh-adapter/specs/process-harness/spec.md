## RENAMED Requirements

### Requirement: Process law has one nucleus and two adapters
- FROM: `Process law has one nucleus and two adapters`
- TO: `Process law has one nucleus and four adapters`

### Requirement: Impeccable detector is on all three clients
- FROM: `Impeccable detector is on all three clients`
- TO: `Impeccable detector is on all four clients`

## MODIFIED Requirements

### Requirement: Process law has one nucleus and four adapters
The process SHALL have a single nucleus and four client adapters. The nucleus is `.cursor/process-fsm.yaml` (T0–T17, I1–I9, 12 column names, events, `context_file`, `enabled_tools` — **not** `product_globs`/`design_globs`), `scripts/process-fsm/`, the canonical skill files, and the short root `AGENTS.md`. Consumer parameters (`product_globs`, `design_globs`, board ids) live in `.covenant-flow/overlay.yaml` and are NOT a second law table. The Cursor adapter is `.cursor/hooks.json`, `.cursor/hooks/*`, `.cursor/rules/harness.mdc`, and `.cursor/commands/`. The Grok adapter is `.grok/hooks/`, generated Moore paging under `.grok/rules/`, and skill stubs under `.grok/skills/`. The OpenCode adapter is `.opencode/plugin/` (auto-loaded `*.js` / `*.ts`), Moore inject via `experimental.chat.system.transform`, and skill stubs under `.opencode/skills/` only for skills the OpenCode 1.18.18 binary does not discover. The dsh adapter is `.dsh/plugin/` (Cordis `apply(ctx)`), Moore inject via `ctx.systemPrompt.section`, and skill stubs under `.dsh/skills/` only for skills dsh does not discover (it discovers `.dsh/skills` and `.agents/skills`, not `.cursor/skills`). A change of column, invariant, or Moore `context_file` text MUST be made once in the yaml (and in a skill only when the change is *how* to work). A change of product glob, design glob, or board ids MUST be made once in the overlay. Adapters SHALL compile law from the yaml and globs/board ids from the overlay. Missing or invalid overlay SHALL fail closed for **product writes**; paging/`sessionStart` remains fail-open (unbound page) and MUST NOT dump the overlay body. Adapters MUST NOT copy T0–T17, I1–I9, or the 12-column runbook. Codex home skills and Hermes skill symlinks MUST NOT be an active contract. The lock machine (`design-planner` lease, packet, `design_artifact_write`, attestation, `opencode.db` as kaizen contract) MUST remain forbidden. `opencode.json` MUST NOT be an active contract of model, MCP, or permission. The fourth harness (dsh) MUST NOT be a source of law: it is a skin, not a second yaml.

#### Scenario: One yaml change reaches four adapters
- **WHEN** a column, invariant, or `context_file` stub is changed in `.cursor/process-fsm.yaml`
- **THEN** the Cursor, Grok, OpenCode, and dsh Guard/paging paths compile that law from the yaml
- **AND** no second copy of the table exists in `.grok/rules/`, `.cursor/rules/`, `.opencode/`, or `.dsh/`

#### Scenario: Dual-write of the law is forbidden
- **WHEN** a reviewer inspects `.cursor/rules/`, `.grok/rules/`, `.opencode/`, and `.dsh/`
- **THEN** none of those directories contains a T0–T17 table, I1–I9 list, or 12-column procedure
- **AND** a Grok, OpenCode, or dsh skill stub MUST NOT contain the runbook copied from `.cursor/skills/`

#### Scenario: Glob change in overlay reaches four Guards
- **WHEN** a product glob is changed in `.covenant-flow/overlay.yaml`
- **THEN** Cursor, Grok, OpenCode, and dsh Guards classify writes using that overlay glob
- **AND** the glob MUST NOT be re-declared as yaml law in packaged `process-fsm.yaml`

#### Scenario: Fourth harness is not the law
- **WHEN** a reviewer inspects `.dsh/` and `scripts/process-fsm/`
- **THEN** `.dsh/` contains only translation (plugin, stubs, patch ids)
- **AND** T0–T17 / I1–I9 remain only in `.cursor/process-fsm.yaml`

### Requirement: Always-on delta lives in AGENTS.md
The short always-on law (resolve `(q, bound_card, q_git)`, chat wording is not authorization, NLU is not δ, `Em Refinamento` is the entry column, `Todo` is not implementation, Design columns must not be skipped, overlay is on-demand, Alan-only T1/T7/T15, T16 is `process_event fechar_release`) SHALL live in the root `AGENTS.md` stub so Cursor, Grok Build, OpenCode, and dsh ingest it. `AGENTS.md` MUST remain at most 40 non-empty lines and MUST point to the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`) for ports/Drive/PostgreSQL/release. It MUST name Cursor Agent, Grok Build, OpenCode, and dsh as clients. It MUST state that Cursor Auto is allowed and that Grok Build, OpenCode, and dsh remain cooperative until their deny essays PASS. It MUST NOT claim Auto OpenCode, Auto Grok, or Auto dsh. It MUST NOT include the 12-column runbook or `release-guard pre`/`post` snippets. The file header MUST NOT say the stub is “não always-on” after this change. Naming dsh in the stub MUST NOT depend on overlay key `clients.dsh`.

#### Scenario: Four clients read the same always-on stub
- **WHEN** a Cursor session, a Grok session, an OpenCode session, and a dsh session start in the repo
- **THEN** all four load root `AGENTS.md`
- **AND** that file states that chat wording is not δ and that `Todo` is not implementation
- **AND** it states Alan-only T1/T7/T15
- **AND** it names Cursor Agent, Grok Build, OpenCode, and dsh
- **AND** it does not claim Grok Auto, OpenCode Auto, or dsh Auto is active
- **AND** it does not contain `scripts/release-guard pre`
- **AND** it names the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`)

### Requirement: Impeccable detector is on all four clients
The Impeccable **detector** SHALL be the same `.agents/skills/impeccable/scripts/hook.mjs` on Cursor, Grok Build, OpenCode, and dsh. Adapters SHALL only translate native events. Cursor remains `.cursor/hooks.json` `afterFileEdit` / `stop` via `.cursor/hooks/impeccable.sh`. Grok SHALL register `PostToolUse` and `Stop` under `.grok/hooks/` mapping to that `hook.mjs` (`afterFileEdit` Cursor maps to `PostToolUse`). OpenCode SHALL register `tool.execute.after` and `session.idle` in the 1.18.18 plugin mapping to the same `hook.mjs`. dsh SHALL register `tools/post-execute` and `agent/turn-stopping` in the Cordis plugin mapping to the same `hook.mjs`. The dsh mapper lives in `dsh_plugin_lib.js` `mapAfterPayload` and MUST read `file_path` first (native envelope), then `path` (`str_replace_editor`); it MUST NOT reuse OpenCode `mapAfterPayload` (that mapper only reads `filePath` / `path` / `patchText` and would leave hook.mjs empty on every dsh UI `write`/`edit`). The detector MUST be fail-open: a finding or a crash of `hook.mjs` MUST NOT abort the turn (dsh MUST NOT return `{ kind: 'block' }` and MUST NOT `steer`). This requirement MUST NOT introduce a second detector, MUST NOT restore the lock machine, and MUST NOT reopen #668 Guard/paging.

#### Scenario: UI edit on any client runs hook.mjs
- **WHEN** a UI file (`frontend/src/**` or equivalent screen file) is edited in Cursor, Grok, OpenCode 1.18.18, or dsh
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

#### Scenario: dsh post-execute maps file_path to hook.mjs
- **WHEN** `tools/post-execute` fires with `exec.name` `write` or `edit` and `arguments.file_path` of a UI file (no `filePath`)
- **THEN** `dsh_plugin_lib.js` `mapAfterPayload` sets hook.mjs stdin `file_path` from that `file_path` and `hook_event_name` equal to `PostToolUse`
- **AND** the mapper MUST NOT be the OpenCode `mapAfterPayload` (which only reads `filePath` / `path` / `patchText`)
- **AND** the listener returns `next()` and does not `{ kind: 'block' }`

#### Scenario: dsh turn-stopping maps to Stop
- **WHEN** `agent/turn-stopping` fires
- **THEN** `hook.mjs` stdin has `hook_event_name` equal to `Stop`
- **AND** the listener does not `steer`

## ADDED Requirements

### Requirement: dsh adapter is plugin skin not a second law
dsh (DeepSeek Harness, Cordis) SHALL be an active client adapter. The versioned skin SHALL live under `.dsh/plugin/` as ESM `apply(ctx)` modules plus `.dsh/cordis.patch.yml` insert ids. The adapter MUST load via a repo helper that passes `dsh web --patch` with **absolute** module `name`s (Cordis entry `name` is literal). `dsh plugin add` into `$DSH_HOME` MUST NOT be the v1 pin channel. The Claude Code hooks bridge (`dsh-hooks-claude-code` / `hooks.json`) MUST NOT be the Guard. Stubs under `.dsh/skills/<name>/SKILL.md` SHALL exist only for process skills dsh does not discover (it discovers `.dsh/skills` and `.agents/skills`, not `.cursor/skills/`). Each stub MUST keep the canonical skill `name`, MUST instruct MUST Read of the canonical `SKILL.md`, MUST keep body (non-empty lines after frontmatter) at most 8 lines, and MUST NOT copy T0–T17. Impeccable (skill) already lives in `.agents/skills/impeccable/` and MUST NOT be duplicated as a second runbook.

#### Scenario: Plugin loads without Claude hooks.json Guard
- **WHEN** dsh starts in the canonical DEV cwd with the versioned helper `--patch`
- **THEN** `.dsh/plugin/process-fsm-guard.js` and `.dsh/plugin/impeccable-hook.js` load
- **AND** Guard deny uses `tools/pre-execute` `{ kind: 'deny' }`
- **AND** no Claude `hooks.json` is the Guard path

#### Scenario: dsh stub is a bridge
- **WHEN** a dsh session needs `covenant-flow`
- **THEN** `.dsh/skills/covenant-flow/SKILL.md` exists
- **AND** its body tells the agent to Read `.cursor/skills/covenant-flow/SKILL.md`
- **AND** the stub body does not contain the 12-column path as a procedure

### Requirement: dsh Auto is gated on the deny essay
Until a human essay on the same worktree shows that an illegal product Write with `q_git=develop` is denied in the dsh session (plugin loaded), dsh MUST be treated as cooperative, not Auto. Grok Build and OpenCode remain cooperative until their own essays PASS. This card MUST NOT inherit Cursor Auto. `process_event` remains the only Agent Status mover in all four clients. Agent MUST NOT `item-edit` Status. dsh `bash` that performs Status `item-edit` MUST be denied by the same Guard.

#### Scenario: Essay not yet green
- **WHEN** the dsh deny essay has not been recorded as PASS
- **THEN** docs and always-on text MUST NOT claim dsh Auto is active
- **AND** the compiled Guard for dsh MUST still deny illegal product writes (the gate is operational claim, not an excuse to skip the adapter)

#### Scenario: process_event is the Status mover in four clients
- **WHEN** a Grok, Cursor, OpenCode, or dsh agent needs to move Project 1 Status
- **THEN** it SHALL call `scripts/process-fsm/process_event.py` with a named event
- **AND** it MUST NOT `gh project item-edit` the Status field
