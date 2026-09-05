# process-harness Specification

## Purpose
Contrato multi-cliente do processo: núcleo = verdade; adapters Cursor, Grok e OpenCode = tradução. Proíbe dual-write da lei.
## Requirements
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
The short always-on law (resolve `(q, bound_card, q_git)`, chat wording is not authorization, NLU is not δ, `Em Refinamento` is the entry column, `Todo` is not implementation, Design columns must not be skipped, overlay is on-demand, Alan-only T1/T7/T15, T16 is `process_event fechar_release`) SHALL live in the root `AGENTS.md` stub so Cursor, Grok Build, OpenCode, and dsh ingest it. `AGENTS.md` MUST remain at most 40 non-empty lines and MUST point to the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`) for ports/Drive/PostgreSQL/release. It MUST name Cursor Agent, Grok Build, OpenCode, and dsh as clients. It MUST state that the four clients are cooperative. It MUST NOT state that Cursor Auto is allowed. It MUST NOT contain `Auto permitido`. It MUST state that Grok Build, OpenCode, and dsh remain cooperative until their deny essays PASS. The deny-essay clause MUST NOT apply to Cursor (Cursor is cooperative by contract). It MUST NOT claim Auto OpenCode, Auto Grok, Auto dsh, or Auto Cursor. It MUST NOT include the 12-column runbook or `release-guard pre`/`post` snippets. The file header MUST NOT say the stub is “não always-on” after this change. Naming dsh in the stub MUST NOT depend on overlay key `clients.dsh`. Overlay `clients.*.auto` MUST NOT interpolate the stub text.

#### Scenario: Four clients read the same always-on stub
- **WHEN** a Cursor session, a Grok session, an OpenCode session, and a dsh session start in the repo
- **THEN** all four load root `AGENTS.md`
- **AND** that file states that chat wording is not δ and that `Todo` is not implementation
- **AND** it states Alan-only T1/T7/T15
- **AND** it names Cursor Agent, Grok Build, OpenCode, and dsh
- **AND** it does not claim Cursor Auto, Grok Auto, OpenCode Auto, or dsh Auto is active
- **AND** it does not contain `Auto permitido`
- **AND** it does not contain `scripts/release-guard pre`
- **AND** it names the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`)

#### Scenario: Yaml auto does not drive the stub
- **WHEN** overlay `clients.cursor.auto` is `true` or `false`
- **THEN** `render_agents()` emits the same hardcoded cooperative client lines
- **AND** the stub still does not contain `Auto permitido`

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

### Requirement: dsh closeout reaches the root through Moore
A change of `context_file[QA]` MUST be made once in `.cursor/process-fsm.yaml`. The dsh plugin SHALL keep injecting that page via its existing Moore section (`runPage` / `covenant-flow:moore`) so the dsh runtime root receives the same-turn T14 / no-QA-child closeout without a second copy of the law in `.dsh/plugin/` or a long stub. Skill text MAY explain the dsh loop; it MUST NOT be the only carrier. Adapters MUST NOT dual-write T0–T17. This requirement MUST NOT add a `decide()` matcher that would deny Cursor `Task` or OpenCode `task`.

#### Scenario: dsh Moore page carries the QA stub
- **WHEN** the dsh plugin builds `covenant-flow:moore` for a bound card with `q=QA`
- **THEN** the injected text contains the yaml `context_file[QA]` stub
- **AND** the plugin source does not contain a second T0–T17 table

#### Scenario: no new decide matcher for QA spawn
- **WHEN** `guard.py` `decide()` is invoked with a Cursor `Task` whose prompt mentions QA or T14
- **THEN** this change MUST NOT add a deny for that tool name

### Requirement: Adapter locators for Impeccable and Grok Guard are cwd-independent
The four client adapters SHALL locate the Impeccable skin without requiring the session working directory to equal the JSON or plugin directory. Grok `.grok/hooks/process-fsm.json` command strings for `PostToolUse`, `Stop`, `PreToolUse`, and `SessionStart` MUST try, in order: (1) the repo-relative path `.grok/hooks/<script>`, (2) the sibling `./<script>` in the current directory, (3) `git rev-parse --show-toplevel` joined with `.grok/hooks/<script>`. Cursor `.cursor/hooks.json` `afterFileEdit` and `stop` MUST use the same class for `.cursor/hooks/impeccable.sh` (repo-relative `.cursor/hooks/`, sibling `./hooks/` or `./`, then git toplevel). The dsh Impeccable plugin MUST call `resolveRepoCwd` (git toplevel of the given cwd, else `REPO_ROOT`) and MUST NOT use `process.cwd() || REPO_ROOT`. The OpenCode Impeccable plugin MUST resolve `input.directory || input.worktree` through git toplevel or `REPO_ROOT` so a session cwd of `$HOME` still invokes `.agents/skills/impeccable/scripts/hook.mjs`. Adapters SHALL only translate native events. The detector remains the same `hook.mjs`. Dual-write of T0–T17 / I1–I9 into `.grok/`, `.dsh/`, or `.opencode/` remains forbidden. The detector MUST stay fail-open: a finding or a crash of `hook.mjs` MUST NOT abort the turn. This requirement MUST NOT reopen #668 / #720 / #782 / #784 / #821, MUST NOT change Guard dsh, and MUST NOT change Cursor `preToolUse` / `beforeShellExecution` / `sessionStart`.

#### Scenario: Grok PostToolUse finds impeccable.sh from three cwds
- **WHEN** the Grok `PostToolUse` command from `.grok/hooks/process-fsm.json` runs via `sh -c` with cwd at the repo root, at `.grok/hooks/`, and at `frontend/`
- **THEN** each invocation exits 0
- **AND** none exits 127 with `./impeccable.sh: not found`

#### Scenario: Grok Stop uses the same locator class
- **WHEN** the Grok `Stop` command from `.grok/hooks/process-fsm.json` runs via `sh -c` with those same three cwds
- **THEN** each invocation exits 0

#### Scenario: Grok Guard and SessionStart do not go mute when cwd is the repo root
- **WHEN** the Grok `PreToolUse` command and the Grok `SessionStart` command run via `sh -c` with cwd at the repo root, at `.grok/hooks/`, and at `frontend/`
- **THEN** each invocation exits 0
- **AND** none exits 127 because `./process-fsm-guard.sh` or `./process-fsm-session-start.sh` was not in the cwd

#### Scenario: Cursor afterFileEdit and stop find impeccable.sh off the JSON directory
- **WHEN** the Cursor `afterFileEdit` and `stop` commands from `.cursor/hooks.json` run via `sh -c` with cwd at the repo root, at `.cursor/`, and at `.cursor/hooks/`
- **THEN** each invocation exits 0

#### Scenario: dsh Impeccable does not treat $HOME as the detector root
- **WHEN** the dsh Impeccable plugin runs with `process.cwd()` equal to `$HOME` (not the consumer git)
- **THEN** `resolveRepoCwd` returns the consumer git toplevel or `REPO_ROOT`
- **AND** the plugin source does not contain `process.cwd() || REPO_ROOT`
- **AND** `hook.mjs` is not invoked with cwd `$HOME`

#### Scenario: OpenCode session directory $HOME still reaches hook.mjs
- **WHEN** the OpenCode Impeccable plugin loads with `input.directory` equal to `$HOME` (and `input.worktree` absent or also `$HOME`)
- **THEN** the detector cwd is the consumer git toplevel or `REPO_ROOT`
- **AND** `.agents/skills/impeccable/scripts/hook.mjs` is the invoked script
- **AND** the turn is not aborted

#### Scenario: Detector remains fail-open
- **WHEN** `hook.mjs` crashes or times out after a tool has already run
- **THEN** the adapter does not abort the turn
- **AND** dsh MUST NOT return `{ kind: 'block' }` and MUST NOT `steer`

#### Scenario: Dual-write of the law stays forbidden
- **WHEN** a reviewer inspects `.grok/hooks/process-fsm.json`, `.dsh/plugin/impeccable-hook.js`, and `.opencode/plugin/impeccable-hook.js` after this change
- **THEN** none contains a T0–T17 table, I1–I9 list, or 12-column procedure
- **AND** `hook.mjs` is still the only detector

### Requirement: dsh always-on stub is ingested when session cwd is not the consumer git root
The short always-on law SHALL remain the consumer root `AGENTS.md` file (compile the file; adapters MUST NOT copy T0–T17 into `.dsh/` or `cordis.yml`). The dsh Guard plugin SHALL inject that file's text through Cordis `ctx.systemPrompt.section` even when the session cwd is not the consumer git root (homologation replay: session `306d48f7-d893-471e-ba4c-8fe7a5153fda`, cwd `/home/ubuntu`). The plugin SHALL resolve the file from adapter `REPO_ROOT` (the git tree that contains `.dsh/plugin/process-fsm-guard.js`), not from `process.cwd()` or `session.header.cwd`. Native `agent-instructions` MAY still load `AGENTS.md` when cwd *is* the repo; that duplication MUST be accepted. The native loader MUST NOT be disabled. Missing or unreadable `AGENTS.md` MUST yield empty section text (fail-open), matching Moore's empty page body. The Guard deny path MUST remain fail-closed. `AGENTS.md` MUST still name Cursor Agent, Grok Build, OpenCode, and dsh, MUST NOT claim Auto dsh, and MUST remain at most 40 non-empty lines. Auto dsh MUST stay gated on a deny essay; this requirement's human essay is the first-request dump containing stub text, not a `skill` tool call.

#### Scenario: Four-client always-on with dsh session cwd not the consumer git
- **WHEN** a Cursor session, a Grok session, and an OpenCode session start in the consumer repo **and** a dsh session starts with session cwd ≠ the consumer git root, plugin loaded via the versioned `--patch` helper, preset `standard`
- **THEN** Cursor, Grok, and OpenCode still ingest root `AGENTS.md` by their existing loaders
- **AND** the dsh first-request system/prompt dump contains the consumer `AGENTS.md` stub text (always-on δ: chat wording is not δ, `Todo` is not implementation)
- **AND** that dump does not contain a T0–T17 table copied into `.dsh/`
- **AND** docs still MUST NOT claim dsh Auto is active

#### Scenario: Replay 306d48f7 injects the stub
- **WHEN** dsh starts as in session `306d48f7-d893-471e-ba4c-8fe7a5153fda` (cwd is not the consumer git, preset `standard`, Guard plugin loaded)
- **THEN** the first-request dump contains the stub file text
- **AND** Moore paging from `covenant-flow:moore` remains present
- **AND** Guard deny of illegal product writes still holds

#### Scenario: Missing AGENTS.md does not fail-open the Guard
- **WHEN** `AGENTS.md` is missing at `REPO_ROOT` and a dsh `write` targets `backend/` with `q_git=develop`
- **THEN** the agents section text is empty
- **AND** if the Guard plugin is loaded it still returns `{ kind: 'deny' }`

### Requirement: dsh process skill catalog is published from the Guard plugin provider
The dsh Guard plugin SHALL publish the process skill catalog from `REPO_ROOT/.dsh/skills` through `ctx.skills.registerProvider` so `dsh-tool-skill` can render `<available_skills>` even when session cwd is not the consumer git root. The provider MUST scan that directory (one level, `<name>/SKILL.md`) regardless of lookup `cwd`. `list(options)` and `get(candidate, options)` MUST return a Promise (thenable). `get` MUST accept the `SkillCandidate` returned by `list`, not a skill name string. Every candidate MUST set `provider` to the provider's `name` (`covenant-flow-process`), plus kebab `name`, non-empty `description`, string `source`, finite `rank`, and boolean `invocation.modelInvocable` / `userInvocable`. A missing skills directory MUST resolve to an empty list (not throw). Invalid frontmatter MUST be skipped in `list`, not thrown. Skill paths MUST NOT appear in `.dsh/cordis.patch.yml`. The host composition row `id: skill-filesystem` that is `disabled: true` MUST NOT be edited by this change. The preset-mounted native `skill-filesystem` MUST remain enabled. Duplicate catalog entries when cwd=repo MUST be accepted. Stubs under `.dsh/skills/` remain bridges (body at most 8 non-empty lines after frontmatter, MUST Read canonical `.cursor/skills/<name>/SKILL.md`, no T0–T17). Human essay for this catalog is first-request `<available_skills>` containing `covenant-flow`; invoking the `skill` tool is not the DoD. Preset `minimal` is out of scope. Unit goldens MUST exercise `list`/`get` through a thenable+`signal` path equivalent to live `waitWithAbort` and `validateCandidate` (not only a synchronous `list()` without `signal`).

#### Scenario: available_skills lists covenant-flow when cwd is not the repo
- **WHEN** a dsh session uses preset `standard`, plugin loaded, session cwd ≠ consumer git root
- **THEN** the first-request dump contains an `<available_skills>` block
- **AND** that block includes `covenant-flow`
- **AND** `.dsh/cordis.patch.yml` does not list `.dsh/skills` or `customSkillDirs`

#### Scenario: Plugin provider lists from REPO_ROOT not session cwd
- **WHEN** the plugin skill provider `list()` runs with lookup `cwd` equal to the user home directory
- **THEN** candidates include `covenant-flow` whose path is under the consumer `REPO_ROOT/.dsh/skills`
- **AND** the provider name is not `filesystem` and is not `runtime`

#### Scenario: Provider thenables survive signal and validateCandidate
- **WHEN** a unit golden calls `list({ cwd, signal })` and `get(candidate, { signal })` with a non-aborted `AbortSignal`
- **THEN** both calls return thenables that fulfill (they MUST NOT return a bare array)
- **AND** each listed candidate has `provider` equal to `"covenant-flow-process"`
- **AND** `validateCandidate` equivalent checks do not throw
- **AND** `get` returns a definition whose `content` is a string and whose `name` matches the candidate

#### Scenario: Native filesystem loader stays
- **WHEN** a reviewer inspects the dsh adapter and the host patch this change ships
- **THEN** the adapter does not disable native project skill discovery
- **AND** it does not change host row `skill-filesystem` from `disabled: true`

### Requirement: dsh Guard denies grill-shaped subagent spawn
The grill-shaped deny SHALL exist **only** as `isGrillShapedSpawn` in `scripts/process-fsm/dsh_plugin_lib.js`, called from `.dsh/plugin/process-fsm-guard.js` in Cordis `tools/pre-execute` **before** `runGuard` / `decide()`. `scripts/process-fsm/guard.py` MUST remain unchanged: its source MUST NOT contain `grill-card`, `dsh_grill_spawn`, or `isGrillShapedSpawn`. The plugin SHALL deny tool names `subagent` and `subagent_fork` when the spawn is **papel de grelha**, not when it is **citação** of a closed grill ritual. Matching SHALL use `String.includes` after `toLowerCase()` (not a regex) and MUST NOT live in `decide()`. Papel: `arguments.description` contains the substring `grill-card`, **or** `arguments.prompt` (or a parse-fail raw arguments string treated as prompt) contains `grill-card` **and** contains none of the pinned citation markers `fronteira vazia`, `do not re-interview`, `não reentrevistar`, `do not invoke grill-card`, `não invocar grill-card`, `closed grill`, `grill-card dod`, `dod grelhado`, `grilled dod`. Citação: description does not contain `grill-card` **and** prompt contains `grill-card` **and** at least one pinned citation marker — this deny MUST NOT fire (`next()` SHALL run). If `arguments` is a JSON string, the plugin SHALL parse it and apply the same fields; parse failure SHALL scan the raw string as prompt. Nested copies SHALL be collected only from `description` and `prompt` keys at any depth (recurse into object values). The helper MUST NOT treat `JSON.stringify` of the whole arguments object as a haystack. A matching papel call MUST return `{ kind: "deny", reason }` containing `dsh_grill_spawn` and MUST NOT call `next()`. `run_in_background` MUST NOT affect the match. Unrelated `subagent` / `subagent_fork` (no needle in description/prompt) MUST call `next()` (fail-open). Tools that are not `subagent` or `subagent_fork` MUST NOT be denied by this heuristic (including Cursor `Task`, Grok `spawn_subagent`, and OpenCode `task` if they appear). Pytest goldens G1–G9 MUST `import { apply }` from `.dsh/plugin/process-fsm-guard.js` and invoke `tools/pre-execute` (same pattern as existing dsh adapter goldens); they MUST NOT pass solely by unit-testing a Python helper inside `decide()`. G12 (Design-author citation allow) MUST use the same `apply` + `pre-execute` path. This deny SHALL be **in addition to** write-like deny and `isCordisRestricted`. `isCordisRestricted` MUST remain `cordis_*` only. The heuristic MUST NOT be a Cursor `preToolUse` matcher and MUST NOT be a Grok hook. The `tools/pre-execute` listener MUST remain registered before `ctx.skills.registerProvider`; a throw from the provider MUST NOT skip deny. Write-deny goldens of the dsh adapter MUST still pass. OpenCode `runGuard` on every `tool.execute.before` remains out of scope for this Task-shaped deny. Grill deny SHALL remain **first** among spawn denys: `isGrillShapedSpawn` before `runGuard`, reason `dsh_grill_spawn`, without `next()` on match. That order is the meaning of «listener unchanged» — the plugin file MUST NOT be required byte-identical to pin `v1.1.6`. Sibling #817 MAY insert `dsh_reasoning_effort_spawn` after grill and before cordis, and MAY add `agent/request` / `agent/request-error`; this change MUST NOT revert those. This requirement MUST NOT reopen #786 (dsh root grills; grill **papel** stays deny; matcher stays out of `guard.py`) and MUST NOT reopen #790.

#### Scenario: G1-G9 go through plugin apply
- **WHEN** pytest goldens G1–G9 run
- **THEN** they `import { apply }` from `.dsh/plugin/process-fsm-guard.js` and call `tools/pre-execute`
- **AND** they MUST NOT pass solely by unit-testing a Python helper inside `decide()`

#### Scenario: grill-card description on subagent is denied
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` with `arguments.description` equal to `grill-card 701`
- **THEN** the listener returns `{ kind: "deny" }` with reason `dsh_grill_spawn`
- **AND** `next()` is not called
- **AND** the deny is returned before `runGuard`

#### Scenario: needle in prompt or mixed case still denies
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent_fork` and only `arguments.prompt` contains `Grill-Card` (ROLE; no pinned citation marker)
- **THEN** the call is denied
- **AND** the same deny holds if `run_in_background` is `false`

#### Scenario: unrelated subagent is fail-open
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` whose description and prompt do not contain `grill-card`
- **THEN** `next()` is called
- **AND** the grill heuristic does not deny

#### Scenario: Cursor-shaped and OpenCode task tools call next
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `Task`, `spawn_subagent`, or OpenCode `task` with `prompt` containing `grill-card`
- **THEN** `next()` is called for each of those tool names
- **AND** the result is not `{ kind: "deny" }` whose reason contains `dsh_grill_spawn`

#### Scenario: write deny still works if registerProvider throws
- **WHEN** `apply(ctx)` throws from `registerProvider` and a later `tools/pre-execute` is an illegal product `edit` or a grill-shaped `subagent`
- **THEN** `apply` itself does not throw
- **AND** both calls return `{ kind: "deny" }`
- **AND** `next()` is not called

#### Scenario: shared decide() does not gain the spawn rule
- **WHEN** a reviewer inspects `scripts/process-fsm/guard.py` and `.cursor/hooks.json` after this change
- **THEN** the source of `guard.py` does not contain `grill-card`, `dsh_grill_spawn`, or `isGrillShapedSpawn`
- **AND** Cursor `preToolUse` matcher is still `Write|StrReplace|Delete|EditNotebook`
- **AND** `isCordisRestricted` still matches only `cordis_*` names

#### Scenario: decide() allows Task with grill-card prompt
- **WHEN** Python `decide()` receives a no-path payload with `tool`/`tool_name` `Task` and `args.prompt` containing `grill-card`
- **THEN** it returns `permission: allow`
- **AND** it MUST NOT invent a new FSM event for this payload

#### Scenario: Design-author citation of closed grill ritual is not this deny
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` with `arguments.description` equal to `design-autor 818` (no `grill-card` in description) and `arguments.prompt` containing `grill-card fronteira vazia`
- **THEN** `next()` is called
- **AND** the result is not `{ kind: "deny" }` whose reason contains `dsh_grill_spawn`

#### Scenario: isolated Apply and reviewer citation is not this deny
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` whose description is `apply 818` or `diff-reviewer 818` and whose prompt cites the grilled DoD (`grill-card dod`, `dod grelhado`, or `closed grill` together with `grill-card`)
- **THEN** `next()` is called
- **AND** the result is not `{ kind: "deny" }` whose reason contains `dsh_grill_spawn`

#### Scenario: nested citation outside description and prompt is not this deny
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` with description `design-autor 818` and a nested non-`description`/non-`prompt` field containing `grill-card`
- **THEN** `next()` is called
- **AND** `isGrillShapedSpawn` is false for that payload
- **AND** a nested `inner.prompt` value `x grill-card y` without a citation marker still makes `isGrillShapedSpawn` true

#### Scenario: grill spawn deny stays first and does not revert sibling #817
- **WHEN** Apply lands this change on a product tip that already has #817 (`dsh_reasoning_effort_spawn` between grill and cordis, plus `agent/request`)
- **THEN** `isGrillShapedSpawn` still runs before `runGuard` and still returns reason `dsh_grill_spawn` without `next()` on papel
- **AND** the #817 gate and `agent/request` listeners remain
- **AND** `.dsh/plugin/process-fsm-guard.js` is not required to match pin `v1.1.6` byte-for-byte

### Requirement: dsh adapter is plugin skin not a second law
dsh (DeepSeek Harness, Cordis) SHALL be an active client adapter. The versioned skin SHALL live under `.dsh/plugin/` as ESM `apply(ctx)` modules plus `.dsh/cordis.patch.yml` insert ids. The adapter MUST load via a repo helper that passes `dsh web --patch` with **absolute** module `name`s. `dsh plugin add` into `$DSH_HOME` MUST NOT be the v1 pin channel. The Claude Code hooks bridge MUST NOT be the Guard. Stubs under `.dsh/skills/<name>/SKILL.md` SHALL exist only for process skills dsh does not discover. Each stub MUST keep the canonical skill `name`, MUST instruct MUST Read of the canonical `SKILL.md`, MUST keep body at most 8 lines, and MUST NOT copy T0–T17.

#### Scenario: Plugin loads without Claude hooks.json Guard
- **WHEN** dsh starts in the canonical DEV cwd with the versioned helper `--patch`
- **THEN** `.dsh/plugin/process-fsm-guard.js` and `.dsh/plugin/impeccable-hook.js` load
- **AND** Guard deny uses `tools/pre-execute` `{ kind: 'deny' }`
- **AND** no Claude `hooks.json` is the Guard path

### Requirement: dsh Auto is gated on the deny essay
Until a human essay on the same worktree shows that an illegal product Write with `q_git=develop` is denied in the dsh session (plugin loaded), dsh MUST be treated as cooperative, not Auto. `process_event` remains the only Agent Status mover in all four clients. Agent MUST NOT `item-edit` Status.

#### Scenario: Essay not yet green
- **WHEN** the dsh deny essay has not been recorded as PASS
- **THEN** docs and always-on text MUST NOT claim dsh Auto is active
- **AND** the compiled Guard for dsh MUST still deny illegal product writes

### Requirement: dsh plugin sanitizes rejected reasoning effort on every model request
The dsh Guard plugin SHALL sanitize reasoning effort in Cordis `agent/request` so the model call MUST NOT send a value this session's chat model rejects (witness: `"none"` / effort off). The sanitizer SHALL live as `sanitizeReasoningEffort` in `scripts/process-fsm/dsh_plugin_lib.js` and SHALL be called from `.dsh/plugin/process-fsm-guard.js` as `ctx.on("agent/request", async (payload, next) => sanitizeReasoningEffort(await next()))`. Sanitizing MUST run after `await next()` so it wins over the runtime `installModelSelection` strip that clears inherited effort when a child descriptor has only `agentProvider`+`agentModel`. Rejected tokens (case-insensitive, trimmed) are `none`, `off`, empty string, and JSON `null`. An already-accepted value in `{minimal, low, medium, high}` SHALL be kept. A missing field or a rejected token SHALL become `reasoningEffort: "high"` (the agent default and the turn-10 witness). Nested `reasoning.effort` SHALL be sanitized the same way and MUST NOT remain `none` beside `reasoningEffort`. The mapping SHALL apply to every provider/model in the dsh session (Q2=A); it MUST NOT be an allowlist of `muse-spark-*`. The mapping SHALL NOT live in `~/.dsh/settings.yaml` as the pin channel and SHALL NOT vendor `deepseek-ai/deepseek-harness`. `scripts/process-fsm/guard.py` `decide()` MUST NOT gain this logic. `inject` MAY stay `["systemPrompt", "skills"]`. Write-like deny, grill-shaped deny, and `isCordisRestricted` MUST still pass.

#### Scenario: Rejected none becomes high
- **WHEN** `sanitizeReasoningEffort` receives `reasoningEffort` equal to `none` or `off` (any case) or nested `reasoning.effort` equal to `none`
- **THEN** the returned config has `reasoningEffort` equal to `high`
- **AND** nested `none` is absent

#### Scenario: Accepted value is kept and missing becomes high
- **WHEN** `sanitizeReasoningEffort` receives `reasoningEffort` equal to `medium`
- **THEN** the returned config keeps `medium`
- **AND** a config with no effort field returns `reasoningEffort` equal to `high`

#### Scenario: Sanitize wins over inherited-effort strip
- **WHEN** `apply(ctx)` registers `agent/request` and an inner waterfall listener strips `reasoningEffort` the way `installModelSelection` does
- **THEN** the config returned to the loop still has `reasoningEffort` equal to `high`
- **AND** a child descriptor that only has provider and model also returns `reasoningEffort` equal to `high`

#### Scenario: Shared decide does not gain the mapper
- **WHEN** a reviewer inspects `scripts/process-fsm/guard.py` after this change
- **THEN** that source does not contain `reasoningEffort` or `dsh_reasoning_effort`
- **AND** `deepseek-ai/deepseek-harness` is not vendored

### Requirement: dsh recovers the root turn on this-class 400 and stops same-preset child spawns after the first child rejection
The plugin SHALL classify this-class rejection with `isReasoningEffortRejection(failure)`: the normalized failure facts contain a reasoning-effort needle (`reasoning.effort` or `reasoningEffort` or `UNSUPPORTED_REASONING_EFFORT`) together with a rejected-token needle (`none` or `off` or `does not support`) or an `INVALID_REQUEST` / `400` together with those needles. Rate-limit, `401`, and Guard deny MUST NOT match. On Cordis `agent/request-error` the payload is `{ agent, turn, step, provider, failure, retryPolicy, signal }`. `payload.provider` is the **LLM provider** (incident witness `opencodealan`) and MUST NOT be used to tell child from root. The **same** agent (session id on `payload.agent`, not `payload.turn` alone) MAY retry once (`{ kind: "retry" }` without `next()`); a second this-class failure on that agent MUST call `next()`. That retry is a model-request recovery, not a new `subagent` spawn and not the #518 empty-spawn retry. A child SHALL be detected **only** from `payload.agent.session.header`: `delegationDepth >= 1` **or** `origin === "subagent"` **or** `parentSession` present. Apply MUST read that header and MUST NOT import `@deepseek-ai/dsh-subagent`. After the first this-class 400 on a child, the plugin SHALL add `header.parentSession` (fallback: caller/root session id) to an in-memory `Set`. Root `tools/pre-execute` SHALL consult that `Set` (the root session is a member) and deny further `subagent` and `subagent_fork` with reason containing `dsh_reasoning_effort_spawn` without `next()`. The gate key MUST NOT be `payload.turn`: that field is the failing agent's turn (isolated child starts at `1`; the incident root was `9`) and is not visible to the other agent's `tools/pre-execute`. A this-class 400 on the **root** (`delegationDepth` 0, no `origin: "subagent"`, no `parentSession`) MUST NOT close that spawn gate (the recovered root MAY spawn the happy-path Apply/reviewer). Listener order in `tools/pre-execute` SHALL be: grill-shaped deny, then this spawn gate, then `isCordisRestricted`, then `runGuard`. The root SHALL record `ERROR: subagent spawn failed/empty` and MAY complete the step itself with an explicit residual; silent fallback remains forbidden. Pytest goldens for the waterfall MUST `import { apply }` from `.dsh/plugin/process-fsm-guard.js`. Golden E7 MUST fire `agent/request-error` on a child with `turn: 1`, `provider: "opencodealan"`, `header.delegationDepth: 1`, `origin: "subagent"`, and a `parentSession`, then `tools/pre-execute` on the **root** with a **different** `turn` (witness `9`) for Apply and reviewer `subagent` calls; it MUST NOT pass with `provider: "spawn"` or with equal turns on both sides.

#### Scenario: Root first this-class 400 retries the same request
- **WHEN** `apply(ctx)` then `agent/request-error` runs for a root agent (`header.delegationDepth` 0, no `parentSession`) with `provider` `opencodealan` and this-class failure for the first time on that agent
- **THEN** the listener returns `{ kind: "retry" }`
- **AND** `next()` is not called

#### Scenario: Second this-class failure on the same agent is terminal
- **WHEN** the same agent (same session id) receives a second `agent/request-error` of this class
- **THEN** `next()` is called
- **AND** the listener does not return `{ kind: "retry" }`

#### Scenario: First child this-class 400 blocks further subagent on the root
- **WHEN** `agent/request-error` runs for a child with `turn` 1, `provider` `opencodealan`, `header.delegationDepth` 1, `origin` `subagent`, and `parentSession` equal to the root session
- **AND** `tools/pre-execute` then runs on the **root** agent with a different `turn` (witness 9) for `subagent` Apply or `subagent` reviewer
- **THEN** both calls return `{ kind: "deny" }` with reason `dsh_reasoning_effort_spawn`
- **AND** `next()` is not called
- **AND** a mock that keys the gate on `payload.turn` or that treats `provider === "spawn"` as the child test MUST fail this scenario

#### Scenario: Root this-class 400 does not close the spawn gate
- **WHEN** `agent/request-error` classifies this class on the root only (`delegationDepth` 0, `provider` `opencodealan`, no `parentSession`)
- **AND** `tools/pre-execute` runs for `subagent` whose description and prompt do not contain `grill-card`
- **THEN** `next()` is called
- **AND** grill-shaped `subagent` is still denied by `dsh_grill_spawn`

#### Scenario: Unrelated failures are not this class
- **WHEN** `isReasoningEffortRejection` receives a 401, a rate-limit, or a Guard deny without reasoning-effort needles
- **THEN** it returns false

