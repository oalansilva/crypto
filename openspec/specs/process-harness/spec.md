# process-harness Specification

## Purpose
Contrato multi-cliente do processo: núcleo = verdade; adapters Cursor, Grok e OpenCode = tradução. Proíbe dual-write da lei.
## Requirements
### Requirement: Process law has one nucleus and two adapters
The process SHALL have a single nucleus and three client adapters. The nucleus is `.cursor/process-fsm.yaml` (T0–T17, I1–I9, 12 column names, events, `context_file`, `enabled_tools` — **not** `product_globs`/`design_globs`), `scripts/process-fsm/`, the canonical skill files, and the short root `AGENTS.md`. Consumer parameters (`product_globs`, `design_globs`, board ids) live in `.covenant-flow/overlay.yaml` and are NOT a second law table. The Cursor adapter is `.cursor/hooks.json`, `.cursor/hooks/*`, `.cursor/rules/harness.mdc`, and `.cursor/commands/`. The Grok adapter is `.grok/hooks/`, generated Moore paging under `.grok/rules/`, and skill stubs under `.grok/skills/`. The OpenCode adapter is `.opencode/plugin/` (auto-loaded `*.js` / `*.ts`), Moore inject via `experimental.chat.system.transform`, and skill stubs under `.opencode/skills/` only for skills the OpenCode 1.18.18 binary does not discover. A change of column, invariant, or Moore `context_file` text MUST be made once in the yaml (and in a skill only when the change is *how* to work). A change of product glob, design glob, or board ids MUST be made once in the overlay. Adapters SHALL compile law from the yaml and globs/board ids from the overlay. Missing or invalid overlay SHALL fail closed for **product writes**; paging/`sessionStart` remains fail-open (unbound page) and MUST NOT dump the overlay body. Adapters MUST NOT copy T0–T17, I1–I9, or the 12-column runbook. Codex home skills and Hermes skill symlinks MUST NOT be an active contract. The lock machine (`design-planner` lease, packet, `design_artifact_write`, attestation, `opencode.db` as kaizen contract) MUST remain forbidden. `opencode.json` MUST NOT be an active contract of model, MCP, or permission.

#### Scenario: One yaml change reaches three adapters
- **WHEN** a column, invariant, or `context_file` stub is changed in `.cursor/process-fsm.yaml`
- **THEN** the Cursor, Grok, and OpenCode Guard/paging paths compile that law from the yaml
- **AND** no second copy of the table exists in `.grok/rules/`, `.cursor/rules/`, or `.opencode/`

#### Scenario: Dual-write of the law is forbidden
- **WHEN** a reviewer inspects `.cursor/rules/`, `.grok/rules/`, and `.opencode/`
- **THEN** none of those directories contains a T0–T17 table, I1–I9 list, or 12-column procedure
- **AND** a Grok or OpenCode skill stub MUST NOT contain the runbook copied from `.cursor/skills/`

#### Scenario: Glob change in overlay reaches three Guards
- **WHEN** a product glob is changed in `.covenant-flow/overlay.yaml`
- **THEN** Cursor, Grok, and OpenCode Guards classify writes using that overlay glob
- **AND** the glob MUST NOT be re-declared as yaml law in packaged `process-fsm.yaml`

### Requirement: Skill stubs are a bridge not a second runbook
Grok SHALL discover process skills via `.grok/skills/<name>/SKILL.md` stubs for every `SKILL.md` directory under `.cursor/skills/` (including `covenant-flow`, `covenant-flow-environments`, `implantar`, `github-project-board`, `kaizen`, and `openspec-*`). Each stub MUST keep the same skill `name`, MUST instruct the agent to Read the canonical `.cursor/skills/<name>/SKILL.md` and follow it (client is Grok Build; map Cursor `Task inherit` to `spawn_subagent` inherit), and MUST NOT copy the runbook body. Stub body (non-empty lines after frontmatter) MUST be at most 8 lines. Stubs MUST be generated from canonical frontmatter plus a fixed body template so description drift is caught in CI. Git mode of canonical skills remains a regular file (not a Hermes symlink). Cursor compatibility scanning `.cursor/skills/` MAY remain enabled; the stub is still the versioned Grok skin because `.grok/skills/` wins name dedup.

#### Scenario: Stub points at the canonical skill
- **WHEN** a Grok session activates `covenant-flow`
- **THEN** `.grok/skills/covenant-flow/SKILL.md` exists
- **AND** its body tells the agent to Read `.cursor/skills/covenant-flow/SKILL.md`
- **AND** the stub body does not contain the 12-column path as a procedure

#### Scenario: Stale stub fails CI
- **WHEN** a canonical skill `description` changes and the stub is not regenerated
- **THEN** the stub generator check in `pytest scripts/process-fsm` fails

### Requirement: Always-on delta lives in AGENTS.md
The short always-on law (resolve `(q, bound_card, q_git)`, chat wording is not authorization, NLU is not δ, `Em Refinamento` is the entry column, `Todo` is not implementation, Design columns must not be skipped, overlay is on-demand, Alan-only T1/T7/T15, T16 is `process_event fechar_release`) SHALL live in the root `AGENTS.md` stub so Cursor, Grok Build, and OpenCode ingest it. `AGENTS.md` MUST remain at most 40 non-empty lines and MUST point to the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`) for ports/Drive/PostgreSQL/release. It MUST name Cursor Agent, Grok Build, and OpenCode as clients. It MUST state that Cursor Auto is allowed and that Grok Build and OpenCode remain cooperative until their deny essays PASS. It MUST NOT claim Auto OpenCode or Auto Grok. It MUST NOT include the 12-column runbook or `release-guard pre`/`post` snippets. The file header MUST NOT say the stub is “não always-on” after this change.

#### Scenario: Three clients read the same always-on stub
- **WHEN** a Cursor session, a Grok session, and an OpenCode session start in the repo
- **THEN** all three load root `AGENTS.md`
- **AND** that file states that chat wording is not δ and that `Todo` is not implementation
- **AND** it states Alan-only T1/T7/T15
- **AND** it names Cursor Agent, Grok Build, and OpenCode
- **AND** it does not claim Grok Auto or OpenCode Auto is active
- **AND** it does not contain `scripts/release-guard pre`
- **AND** it names the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`)

### Requirement: Grok Auto is gated on the deny essay
Until a human essay on the same worktree shows that an illegal product Write with `q_git=develop` is denied in **both** Cursor and Grok Build, Grok Build MUST be treated as cooperative, not Auto. `process_event` remains the only Agent Status mover in both clients. Agent MUST NOT `item-edit` Status.

#### Scenario: Essay not yet green
- **WHEN** the Grok deny essay has not been recorded as PASS
- **THEN** docs and always-on text MUST NOT claim Grok Auto is active
- **AND** the compiled Guard for Grok MUST still emit `decision: deny` on illegal product writes (the gate is operational claim, not an excuse to skip the adapter)

#### Scenario: process_event is the Status mover in both clients
- **WHEN** a Grok or Cursor agent needs to move Project 1 Status
- **THEN** it SHALL call `scripts/process-fsm/process_event.py` with a named event
- **AND** it MUST NOT `gh project item-edit` the Status field

### Requirement: Grok stubs exist for design-critic and Impeccable
Grok SHALL have thin skill stubs at `.grok/skills/design-critic/SKILL.md` and `.grok/skills/impeccable/SKILL.md`. Each stub MUST keep the canonical skill `name`, MUST instruct MUST Read of `.agents/skills/<name>/SKILL.md`, MUST map Cursor `Task inherit` to `spawn_subagent` inherit, MUST NOT copy the runbook, and MUST keep body (non-empty lines after frontmatter) at most 8 lines. `scripts/process-fsm/grok_stubs.py` SHALL generate and CI-check these extras in addition to stubs for `.cursor/skills/*/SKILL.md`. A missing or stale extra stub MUST fail the stub generator check. The hop of reading stub then canonical is accepted for Grok only. After unique pin, Cursor-skill stubs SHALL use `covenant-flow` names, not `alan-workflow`.

#### Scenario: Grok Design loads design-critic via stub
- **WHEN** a Grok session runs Design
- **THEN** `.grok/skills/design-critic/SKILL.md` exists
- **AND** its body tells the agent to Read `.agents/skills/design-critic/SKILL.md`
- **AND** the stub body does not contain the Impeccable pipeline as a copied procedure

#### Scenario: Extra stub drift fails CI
- **WHEN** `.agents/skills/impeccable/SKILL.md` description changes and the Grok stub is not regenerated
- **THEN** the stub generator check in `pytest scripts/process-fsm` fails

#### Scenario: Cursor skills stubs remain a bridge
- **WHEN** a reviewer inspects `.grok/skills/covenant-flow/SKILL.md` on a uniquely pinned consumer
- **THEN** it points at `.cursor/skills/covenant-flow/SKILL.md`
- **AND** extra `.agents` stubs do not replace that generator path
- **AND** `.grok/skills/alan-workflow/` is not the canonical stub after unique pin

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
- **WHEN** an OpenCode session needs `covenant-flow`
- **THEN** `.opencode/skills/covenant-flow/SKILL.md` exists
- **AND** its body tells the agent to Read `.cursor/skills/covenant-flow/SKILL.md`
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

### Requirement: Guard and paging read consumer overlay not a second law
`decide()` SHALL load consumer parameters (`product_globs`, `design_globs`, board ids, `canonical_paths`, `forbidden_worktrees`) from `.covenant-flow/overlay.yaml`. `page()` MAY read the same overlay for tuple/context but missing overlay MUST NOT abort the turn: paging/`sessionStart` remains fail-open with an unbound page and MUST NOT dump the overlay body. Column **names**, events, T0–T17, and I1–I9 SHALL remain only in `process-fsm.yaml`. Dual-write of that table into `.grok/rules/`, `.cursor/rules/`, `.opencode/`, or the overlay MUST remain forbidden. Missing or invalid overlay SHALL fail closed for **product writes** only.

#### Scenario: Globs come from overlay
- **WHEN** `product_globs` in `.covenant-flow/overlay.yaml` lists a consumer product path
- **THEN** Guard classifies writes to that path as product writes
- **AND** the packaged yaml does not hardcode Cripto-only globs as the portable law

#### Scenario: Dual-write of the law stays forbidden after packaging
- **WHEN** a reviewer inspects `.grok/rules/`, `.opencode/`, and `.covenant-flow/overlay.yaml`
- **THEN** none contains a T0–T17 table or I1–I9 list
- **AND** adapters still compile from the single yaml nucleus

#### Scenario: Missing overlay fail-closes writes not paging
- **WHEN** overlay is absent and a product-path Write is attempted
- **THEN** Guard denies the write
- **AND** `sessionStart`/`page()` still emits an unbound page without dumping `overlay_doc`

