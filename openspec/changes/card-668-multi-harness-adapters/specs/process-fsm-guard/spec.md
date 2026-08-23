## ADDED Requirements

### Requirement: Guard normalizes Cursor and Grok envelopes
`scripts/process-fsm/` SHALL normalize hook stdin so `decide()` is client-agnostic. The normalizer MUST accept Cursor keys (`tool_name`, `tool_input`, `command`, `cwd`) and Grok keys (`toolName`, `toolInput`, `workspaceRoot`, camelCase equivalents) and MUST treat missing keys as empty rather than crashing. `cwd` MUST fall back to `workspaceRoot` when absent. Canonical write tools SHALL include `Write`, `StrReplace`, `Delete`, `EditNotebook`, `write`, `search_replace`, `Edit`, `MultiEdit`. Canonical shell tools SHALL include `Shell`, `Bash`, `run_terminal_command`, `run_terminal_cmd`. Path extraction MUST use `path` / `file_path` / `file` / `target_file` / `target_notebook` from the normalized tool input. A Grok `search_replace` or `write` of a `product_globs` path with `q_git=develop` MUST take the same `write_produto` path as a Cursor `Write`. The bash fallback MUST parse the same Grok keys; missing camelCase parse is not an allow token.

#### Scenario: Grok write of product on develop is denied
- **WHEN** stdin is a Grok `PreToolUse` envelope with `toolName=write` (or `search_replace`) and `toolInput.file_path` under `backend/` or `frontend/src/`, and `q_git=develop`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: Cursor Write still denied on develop
- **WHEN** stdin is a Cursor `preToolUse` `Write` of `backend/app/tasks/discovery_tasks.py` with `q_git=develop`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: Grok shell tee onto backend is denied
- **WHEN** stdin is a Grok `run_terminal_command` whose `toolInput.command` redirects or `tee`s onto a `product_globs` path and I1 does not hold
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: Grok OpenSpec write in Design on card branch is allowed
- **WHEN** stdin is Grok `search_replace` of a path under `openspec/changes/` and `status` is `Design` and `q_git` matches `card-<id>-*`
- **THEN** the Guard returns `permission: allow` and `decision: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path

### Requirement: Guard emit is dual Cursor and Grok
Every Guard stdout object (Python `decide()` and the bash fallback in the hook adapter) MUST include both Cursor keys (`permission`, `agent_message`, `user_message`) and Grok keys (`decision`, `reason`). `permission`/`decision` MUST be the same allow-or-deny. Deny MUST set `reason` to a non-empty string (the same text as `agent_message` is allowed). Allow MAY use `decision: allow` with empty `reason`. The adapter MUST still emit this dual JSON if PyYAML fails. Grok's product-level fail-open on hook crash is an accepted residual; the adapter MUST NOT rely on it (it MUST emit valid `decision: deny` for product paths in the fallback).

#### Scenario: Dual keys on deny
- **WHEN** `decide()` denies a product write
- **THEN** stdout JSON has `permission` equal to `deny` and `decision` equal to `deny`
- **AND** `agent_message` and `reason` are non-empty

#### Scenario: Dual keys on allow
- **WHEN** `decide()` allows a design-glob write on `card-<id>-*`
- **THEN** stdout JSON has `permission` equal to `allow` and `decision` equal to `allow`

#### Scenario: Bash fallback dual-emits
- **WHEN** the Python Guard is unavailable and the path is `backend/` or `frontend/src/`
- **THEN** the bash fallback prints JSON containing `permission: deny` and `decision: deny`

#### Scenario: Bash fallback parses Grok envelope
- **WHEN** the Python Guard is unavailable and stdin is Grok `toolName=write` with `toolInput.file_path` under `backend/`
- **THEN** the bash fallback prints JSON containing `permission: deny` and `decision: deny`
- **AND** it MUST NOT take the missing-path allow

### Requirement: Grok registers the same Guard
`.grok/hooks/` SHALL register a `PreToolUse` command hook whose matcher covers write tools (`Write|StrReplace|Delete|EditNotebook|write|search_replace|Edit|MultiEdit`) and shell tools (`Bash|Shell|run_terminal_command|run_terminal_cmd`), invoking the same Guard scripts as Cursor. Nested Grok JSON (`hooks: [{type, command}]`) MUST be used. `timeout` on those PreToolUse handlers MUST be at least 30 seconds (product default is 5s fail-open). Project hooks require folder trust (`/hooks-trust` or `--trust`); homologation MUST record that trust. Double invocation with Cursor-compat loading of `.cursor/hooks.json` is allowed: `decide()` is idempotent and the first `deny` wins. The Guard MUST still deny Status `item-edit` and `.design-digest` mutation on the Grok shell path.

#### Scenario: Grok hooks file exists
- **WHEN** `.grok/hooks/` is loaded in a trusted folder
- **THEN** a `PreToolUse` matcher covers `write` or `search_replace` and the Cursor aliases `Write`/`Edit`
- **AND** a `PreToolUse` matcher covers `run_terminal_command` and `run_terminal_cmd`
- **AND** the command invokes `scripts/process-fsm/guard.py` (directly or via a thin adapter)
- **AND** the write/shell handlers set `timeout` ≥ 30

#### Scenario: Grok Status item-edit is denied
- **WHEN** `run_terminal_command` contains `gh project item-edit` and the Project 1 Status field id
- **THEN** the Guard returns `decision: deny`
- **AND** `reason` tells the Agent to use `process_event`
