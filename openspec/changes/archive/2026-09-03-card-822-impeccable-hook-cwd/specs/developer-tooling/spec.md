## ADDED Requirements

### Requirement: Versioned hook commands find Impeccable adapters off the JSON directory
Versioned developer-tooling skins SHALL invoke the same `.agents/skills/impeccable/scripts/hook.mjs` when the client working directory is the repo root, the JSON/plugin directory, or another directory inside the consumer git. Grok commands in `.grok/hooks/process-fsm.json` MUST NOT be a bare `./impeccable.sh` / `./process-fsm-*.sh` that only works when cwd is `.grok/hooks/`. Cursor `.cursor/hooks.json` `afterFileEdit` / `stop` MUST NOT be a path that only works when cwd is the repo root. dsh `.dsh/plugin/impeccable-hook.js` MUST resolve the consumer git (or `REPO_ROOT`) instead of trusting a filled-in `process.cwd()`. OpenCode `.opencode/plugin/impeccable-hook.js` MUST harden `input.directory || input.worktree || REPO_ROOT` so cwd `$HOME` does not miss `hook.mjs`. The pele only translates the native event. This is not a second detector. `git ls-files` of the four skins MUST still include those adapter files. Cursor Guard / dsh Guard / `hook.mjs` internals stay out of this requirement.

#### Scenario: Grok JSON no longer depends on JSON-dir cwd
- **WHEN** `.grok/hooks/process-fsm.json` is loaded
- **THEN** `PostToolUse` and `Stop` command strings contain `.grok/hooks/impeccable.sh` and a `test -f` of that repo-relative path
- **AND** they still mention `./impeccable.sh` as the sibling fallback
- **AND** they mention `git rev-parse --show-toplevel`
- **AND** `PreToolUse` and `SessionStart` use the same locator class for `process-fsm-guard.sh` and `process-fsm-session-start.sh`

#### Scenario: Cursor hooks.json Impeccable is the same locator class
- **WHEN** `.cursor/hooks.json` is loaded
- **THEN** `afterFileEdit` and `stop` command strings contain `.cursor/hooks/impeccable.sh` and a `test -f` of that repo-relative path
- **AND** they mention `git rev-parse --show-toplevel`
- **AND** `preToolUse` / `beforeShellExecution` remain `.cursor/hooks/process-fsm-guard.sh`
- **AND** `sessionStart` remains `.cursor/hooks/process-fsm-session-start.sh`

#### Scenario: dsh plugin exports resolveRepoCwd
- **WHEN** `scripts/process-fsm/dsh_plugin_lib.js` and `.dsh/plugin/impeccable-hook.js` are inspected
- **THEN** the lib exports `resolveRepoCwd`
- **AND** the plugin calls `resolveRepoCwd(process.cwd())` as the detector cwd
- **AND** the plugin does not contain `process.cwd() || REPO_ROOT`

#### Scenario: OpenCode plugin does not take $HOME as detector root
- **WHEN** `.opencode/plugin/impeccable-hook.js` loads with `directory` `$HOME`
- **THEN** `runHookMjs` receives the consumer git toplevel or `REPO_ROOT`, not `$HOME`
- **AND** `hook.mjs` exists at `.agents/skills/impeccable/scripts/hook.mjs` relative to that root

#### Scenario: UI edit still fail-open on four clients
- **WHEN** a frontend file is edited in Cursor, Grok, OpenCode 1.18.18, or dsh
- **THEN** the same `hook.mjs` is the detector
- **AND** a detector finding does not abort the session
