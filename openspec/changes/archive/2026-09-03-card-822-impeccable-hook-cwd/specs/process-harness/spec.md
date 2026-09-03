## ADDED Requirements

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
