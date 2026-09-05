# process-fsm-guard Specification

## Purpose
Guard Write do Cursor: compila `.cursor/process-fsm.yaml` + resolver e deny/allow `Write`/`StrReplace`/`Delete`/`EditNotebook` (e shell mutante) de produto antes do side-effect.
## Requirements
### Requirement: Guard compiles yaml and resolver before product writes
`scripts/process-fsm/` SHALL expose a Guard that, given a Cursor hook stdin JSON, extracts the path from the Cursor envelope, classifies it against overlay `.covenant-flow/overlay.yaml` `product_globs` / `design_globs` **before** calling `evaluate()`, and uses the resolver for `(q, bound_card, q_git)`. Event `write_produto` MUST be sent to `evaluate()` only when the path matches overlay `product_globs`. Paths outside overlay `product_globs` MUST return `permission: allow` when `status` is readable (including OpenSpec and prototype writes in Design), **except** (a) Shell commands classified as Project Status edits and (b) any `Write`/`StrReplace`/`Delete` whose path ends with `.design-digest`, or Shell classified as **mutating** a `.design-digest` path (any `q`; classified **before** overlay `design_globs` glob-first). Exception (b) MUST NOT fire solely because the substring `.design-digest` appears in a non-mutating Shell command (including `git add`, `git commit`, `git status`, or `git reset` that only cite the filename). The packaged yaml MUST NOT be the source of those globs. The Guard MUST NOT invent transitions, MUST NOT move Project Status, and MUST NOT replace the Impeccable adapter. Dual-write of T0–T17 / I1–I9 remains forbidden.

Fixtures MUST use the live Cursor envelope, not an internal dict that skips the parser:
- `preToolUse`: `tool_name`, `tool_input` (`path` / `file_path` / `file` / `target_notebook`), `cwd`; tests MAY inject `status`.
- `beforeShellExecution`: `command`, `cwd`; tests MAY inject `status`.

#### Scenario: Product write allowed under I1
- **WHEN** stdin JSON is a `Write` (or `StrReplace`/`Delete`/`EditNotebook`) of an overlay `product_globs` path, `status` is `Em desenvolvimento` or `Code Review`, `q_git` is `card-<id>-*`, and `bound_card` equals that id
- **THEN** the Guard returns `permission: allow`

#### Scenario: Illegal product write is denied
- **WHEN** stdin JSON is a product `Write` and any of Todo, Design, Aprovação de Design, Pronto para Dev, QA, Done, Homologado, Pronto, Cancelado, `q_git=develop`, `q_git=main`, or `bound_card=⊥` holds
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` names the reason (`I1`, `I3`, illegal_edge id, or unbound)

#### Scenario: I3 two-phase apply
- **WHEN** `status` is `Pronto para Dev` and the tool writes an overlay `product_globs` path even with `q_git=card-<id>-*` and matching `bound_card`
- **THEN** the Guard returns `permission: deny`
- **AND** allow happens only after `status` is already `Em desenvolvimento`

#### Scenario: Replay b6a71170
- **WHEN** the fixture is `Write` of `backend/app/tasks/discovery_tasks.py` with `q_git=develop` and overlay `product_globs` includes that path
- **THEN** the Guard returns `permission: deny`

#### Scenario: Design OpenSpec write is not write_produto
- **WHEN** stdin is `preToolUse` `Write` of a path under `openspec/changes/` (or `frontend/public/prototypes/`) and `status` is `Design` and `q_git` matches `card-<id>-*`
- **THEN** the Guard returns `permission: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path
- **AND** the path does not end with `.design-digest`

#### Scenario: Sidecar write is denied even under design_globs
- **WHEN** stdin is `preToolUse` `Write` (or `StrReplace`/`Delete`) of `openspec/changes/<change>/.design-digest` with a file path present and `status` is `Design` (or any other `q`)
- **THEN** the Guard returns `permission: deny`
- **AND** it MUST classify the sidecar **before** the overlay `design_globs` allow

#### Scenario: Git cite of sidecar is not denied by substring
- **WHEN** `beforeShellExecution` stdin `command` is `git add`, `git commit`, `git status`, or `git reset` that mentions `.design-digest` only as a path or message cite (no write/redirect/`rm`/python open-write of the sidecar)
- **THEN** the Guard MUST NOT return `permission: deny` for reason `sidecar`

#### Scenario: Classification uses overlay globs not yaml
- **WHEN** overlay `product_globs` lists a consumer path that is absent from packaged `process-fsm.yaml`
- **THEN** `decide()` classifies that path as product write
- **AND** the packaged yaml is not consulted for glob membership

### Requirement: Guard denies Agent Status item-edit
The Guard `beforeShellExecution` **and** `preToolUse` paths SHALL classify `.design-digest` **mutations** and Status board edits **before** the missing-path early-return and **before** overlay `design_globs` glob-first allow. It SHALL deny a Cursor Shell command that edits Project `Status` via `gh project item-edit` (Status field id from overlay `board.status_field_id`, or a `--single-select-option-id` that is a Status option id from overlay `board.status_options`) or via GraphQL `updateProjectV2ItemFieldValue` targeting that field, **even when** the same `command` string also contains `process_event.py`. The packaged Guard MUST NOT hardcode Cripto field id `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM`. A Shell command that is **only** a python invocation of `scripts/process-fsm/process_event.py` plus a named event and flags MUST be allowed by this Status-edit rule. The Guard MUST deny `Write`/`StrReplace`/`Delete` whose path ends with `.design-digest`. The Guard MUST deny Shell classified as mutating a `.design-digest` path (redirect/`tee` onto the sidecar, `rm`/`unlink` of the sidecar, `cp`/`mv`/`install` with sidecar destination, `sed -i`/`perl -i` on the sidecar, or `python`/`python3 -c` that opens/writes the sidecar). The Guard MUST NOT deny Shell solely because `.design-digest` appears as a substring without such mutation (including git cite). The bash fallback in `.cursor/hooks/process-fsm-guard.sh` MUST apply the same Status-edit and sidecar-mutation denies before allowing commands that have no file path and before any `design_globs` allow. The Guard MUST NOT honor `PROCESS_FSM_MOVE` or any environment allow. The Guard MUST still NOT itself move Project Status. `git commit`, `git push`, and `./restart` remain out of scope as product-write hooks (they MUST still not be denied merely for citing `.design-digest`). Dual-write of the law remains forbidden.

#### Scenario: Direct item-edit of Status is denied
- **WHEN** `beforeShellExecution` stdin `command` contains `gh project item-edit` and the overlay `board.status_field_id`, even if no file `path` is present
- **THEN** the Guard returns `permission: deny`
- **AND** it MUST NOT take the missing-path early-return allow
- **AND** `agent_message` tells the Agent to use `process_event`

#### Scenario: process_event CLI is allowed
- **WHEN** `command` is solely a python invocation of `scripts/process-fsm/process_event.py` with a named event and optional flags (no `item-edit` / GraphQL Status in the same string)
- **THEN** this Status-edit rule does not deny the command

#### Scenario: Chained process_event and item-edit is denied
- **WHEN** `command` contains both `process_event.py` and `gh project item-edit` with the overlay Status field id
- **THEN** the Guard returns `permission: deny`

#### Scenario: Sidecar write is denied
- **WHEN** stdin is `Write` or mutating shell of a path ending in `.design-digest`
- **THEN** the Guard returns `permission: deny`

#### Scenario: Python -c open-write of sidecar is denied
- **WHEN** `beforeShellExecution` stdin `command` is a `python`/`python3 -c` that opens a `.design-digest` path for write
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` names reason `sidecar`

#### Scenario: Git add citing sidecar is allowed by sidecar rule
- **WHEN** `beforeShellExecution` stdin `command` is `git add` of a path ending in `.design-digest` (no mutation token writing the file contents)
- **THEN** the Guard MUST NOT deny for reason `sidecar`

#### Scenario: Read-only gh remains allowed
- **WHEN** `command` is `gh issue view 612` or `gh project item-list` without `item-edit`
- **THEN** the Guard does not deny because of the Status-edit rule

#### Scenario: Packaged Guard has no hardcoded Cripto field id
- **WHEN** the product Guard sources are inspected
- **THEN** they do not contain `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM` as a packaged constant
- **AND** Status-edit matching uses overlay `board.status_field_id` and `board.status_options` ids

### Requirement: Fail-closed is asymmetric
If `status`/`q` is missing, unreadable, or a Status provider times out, the Guard MUST deny overlay `product_globs` writes and MUST allow writes whose path matches overlay `design_globs` when the path worktree branch already matches `card-<id>-*`. If `.covenant-flow/overlay.yaml` is missing or invalid, the Guard MUST deny product writes (fail-closed) and MUST NOT treat missing overlay as allow. Unit tests MUST inject `status` in the stdin JSON and MUST NOT call GitHub.

#### Scenario: Status unreadable, product path
- **WHEN** stdin omits `status` and the Status provider returns nothing, and the path matches overlay `product_globs`
- **THEN** permission is `deny`

#### Scenario: Status unreadable, design path on card branch
- **WHEN** stdin omits `status` and the path is under `openspec/changes/` or `frontend/public/prototypes/` and `q_git` matches `card-<id>-*`
- **THEN** permission is `allow`

#### Scenario: Fixtures without GitHub
- **WHEN** `pytest scripts/process-fsm -q` runs
- **THEN** Guard fixtures execute from stdin-like JSON using injected `status` and fake worktrees or stubs
- **AND** no network call to GitHub is made

#### Scenario: Missing overlay denies product writes
- **WHEN** overlay is absent or fails schema and stdin is a product-path `Write`
- **THEN** permission is `deny`
- **AND** missing overlay is not an allow token

### Requirement: Shell writes use the same deny as Write
`.cursor/hooks.json` SHALL register `beforeShellExecution` on the same Guard adapter. That hook SHALL apply the same deny as `Write` for commands classified as mutating a `product_globs` path (shell redirection, `tee`, `sed -i`, copy/move onto a product path). Commands that only read or test product trees (`pytest`, `ruff`, `git status`) MUST be allowed. Commands classified as Project Status `item-edit` / Status GraphQL MUST be denied (card #612). Sidecar classification MUST use mutation detection (card #631), not substring-only deny. `git commit`, `git push`, and `./restart` remain out of scope as product-write hooks.

#### Scenario: Redirect onto backend
- **WHEN** `beforeShellExecution` stdin has `command` that redirects or `tee`s onto `backend/app/main.py` and I1 does not hold
- **THEN** permission is `deny`

#### Scenario: Pytest is not a write
- **WHEN** `command` is `pytest backend/ -q` (or equivalent test runner) without a mutation token
- **THEN** permission is `allow`

#### Scenario: beforeShellExecution covers sidecar false positive and true deny
- **WHEN** fixtures exercise `beforeShellExecution` with (1) `git add`/`git commit`/`git status` citing `.design-digest` and (2) a mutating shell of `.design-digest`
- **THEN** (1) is not denied for reason `sidecar` and (2) is denied for reason `sidecar`

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

### Requirement: Guard normalizes the OpenCode native dialect
`scripts/process-fsm/` SHALL normalize hook stdin so `decide()` is client-agnostic across three dialects. In addition to Cursor (`tool_name` / `tool_input`) and Grok (`toolName` / `toolInput`), the normalizer MUST accept the native OpenCode payload `{ tool, args }` as a third dialect. Canonical OpenCode write tools SHALL include `write`, `edit`, and `apply_patch`. Canonical OpenCode shell tool SHALL include `bash`. Path extraction MUST use `args.filePath` for `write`/`edit`. For `apply_patch`, path extraction MUST parse `args.patchText` markers observed on OpenCode 1.18.18: `*** Add File:`, `*** Update File:`, `*** Delete File:`, and `*** Move to:` (issue shorthand “Move File” maps to live `*** Move to:`; `*** Move to:` yields the **destination** path). `extract_paths()` SHALL return every marker path in order. `decide()` SHALL classify each extracted path and treat the envelope as `write_produto` when **any** path matches `product_globs`. For `bash`, path extraction MUST use `args.command` with the same mutation classification as other shell dialects (`tee`, `>`, Status `item-edit`). `cwd` MAY come from plugin `directory` / `worktree` when the envelope omits `cwd`. An OpenCode `edit`/`write` of a `product_globs` path with `q_git=develop` MUST take the same `write_produto` path as a Cursor `Write`. Unknown tools remain class #611: allow. The bash fallback MUST parse `tool`/`args`/`filePath`/`patchText`; missing native keys is not an allow token for those canonical OpenCode write tools.

#### Scenario: OpenCode edit of product on develop is denied
- **WHEN** stdin is a native OpenCode envelope `{ "tool": "edit", "args": { "filePath": "backend/app/tasks/discovery_tasks.py" } }` and `q_git=develop`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: OpenCode apply_patch of product on develop is denied
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "*** Begin Patch\n*** Update File: backend/app/main.py\n*** End Patch" } }` and `q_git=develop`
- **THEN** `extract_paths()` equals `["backend/app/main.py"]`
- **AND** the Guard returns `permission: deny` and `decision: deny`
- **AND** the deny is `write_produto`, not empty-path

#### Scenario: OpenCode apply_patch OpenSpec path from patchText is allowed
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "*** Begin Patch\n*** Add File: openspec/changes/card-720-opencode-three-adapters/design.md\n*** End Patch" } }` with no `filePath`, `status` is `Design`, and `q_git` matches `card-720-*`
- **THEN** `extract_paths()` equals `["openspec/changes/card-720-opencode-three-adapters/design.md"]`
- **AND** the Guard returns `permission: allow` and `decision: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path

#### Scenario: OpenCode apply_patch Move to product dest is denied
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "*** Begin Patch\n*** Update File: docs/note.md\n*** Move to: backend/app/moved.py\n*** End Patch" } }` and `q_git=develop`
- **THEN** `extract_paths()` contains `backend/app/moved.py`
- **AND** the Guard returns `permission: deny` and `decision: deny`
- **AND** a parse that only kept `docs/note.md` MUST NOT be treated as passing this scenario

#### Scenario: OpenCode bash tee onto backend is denied
- **WHEN** stdin is `{ "tool": "bash", "args": { "command": "echo x | tee backend/app/main.py" } }` and I1 does not hold
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: OpenCode OpenSpec write in Design on card branch is allowed
- **WHEN** stdin is OpenCode `edit` of a path under `openspec/changes/` and `status` is `Design` and `q_git` matches `card-<id>-*`
- **THEN** the Guard returns `permission: allow` and `decision: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path

#### Scenario: Unknown OpenCode tool remains allow
- **WHEN** stdin is `{ "tool": "grep", "args": {} }` with no extractable product path
- **THEN** the Guard returns `permission: allow` (class #611)

### Requirement: Empty OpenCode write path is not allow
When the canonical tool is OpenCode `write`, `edit`, or `apply_patch`, a missing `filePath`, empty `patchText`, or `patchText` with no extractable path MUST NOT return allow. The Guard MUST deny (not take the missing-path early-return allow used for unknown tools). Cursor/Grok envelopes whose tool is not in that OpenCode write set keep the existing missing-path behavior except Status-edit and sidecar mutation.

#### Scenario: apply_patch with empty patchText is denied
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "" } }`
- **THEN** the Guard returns `permission: deny` and `decision: deny`
- **AND** it MUST NOT take the missing-path early-return allow

#### Scenario: apply_patch without extractable path is denied
- **WHEN** stdin is `{ "tool": "apply_patch", "args": { "patchText": "*** Begin Patch\n*** End Patch" } }`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: edit with empty filePath is denied
- **WHEN** stdin is `{ "tool": "edit", "args": { "filePath": "" } }`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

### Requirement: OpenCode plugin throws on Guard deny
The OpenCode adapter SHALL live in `.opencode/plugin/` as auto-loaded JS (or TS) and SHALL serialize the native `{ tool, args }` object, invoke the same `scripts/process-fsm/guard.py` / `decide()`, and **throw** when `permission`/`decision` is deny. OpenCode 1.18.18 MUST NOT be treated as honoring stdout JSON `{permission, decision}`. Allow MUST NOT throw. Detector hooks MUST NOT share this throw path. `process_event` remains the only Status mover; OpenCode `bash` with Status `item-edit` MUST throw via this deny.

#### Scenario: Plugin throw on illegal product write
- **WHEN** the plugin receives `tool.execute.before` for `edit` of `backend/` with `q_git=develop`
- **THEN** it calls `decide()` with the native envelope
- **AND** it throws (does not return JSON `{permission: deny}` as the OpenCode decision)

#### Scenario: Plugin does not throw on Design OpenSpec write
- **WHEN** the plugin receives `tool.execute.before` for `edit` of `openspec/changes/` with `status=Design` and `q_git=card-<id>-*`
- **THEN** it does not throw

### Requirement: Shared board_status module reads overlay ids
`scripts/process-fsm/board_status.py` SHALL be the single module that supplies Status field id and Status option ids to both the Guard and the `process_event` mover. It SHALL load `board.status_field_id` and `board.status_options` ids from `.covenant-flow/overlay.yaml`. Packaged Python (`board_status.py`, `guard.py`, `process_event.py`) MUST NOT hardcode Cripto field id `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM`. Missing or invalid overlay SHALL fail closed for product writes and for live Status moves that need those ids; paging remains fail-open.

#### Scenario: Packaged Python has no hardcoded Cripto field id
- **WHEN** product sources `scripts/process-fsm/board_status.py`, `guard.py`, and `process_event.py` are inspected
- **THEN** none contains `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM` as a packaged constant
- **AND** Guard Status-edit and the `process_event` mover both resolve ids through `board_status` from overlay

#### Scenario: process_event mover uses overlay Status ids
- **WHEN** `process_event()` performs a legal Status move
- **THEN** the mover targets overlay `board.status_field_id` and the matching `board.status_options` id for the destination column name
- **AND** it does not use a hardcoded Cripto Project field id

### Requirement: Guard denies card-branch checkout on the canonical DEV source
The Guard `beforeShellExecution` path (and the bash fallback) SHALL classify, **before** the missing-path early-return, a command that creates a `card-*` branch on overlay `environments.dev.source`. It MUST deny `git checkout -b card-*`, `git checkout --track -b card-*`, and `git switch -c card-*` when `cwd` or `git -C` resolves to that source path. The deny `reason` SHALL be `canonical_card_branch`. The same command in a worktree that is not the canonical source MUST NOT be denied by this rule. `git checkout` of an existing branch, `git worktree add`, and `git status` MUST NOT be denied by this rule. The packaged Guard MUST read the source path from overlay `environments.dev.source`, not a hardcoded string in the requirement tests' production module as the only source of truth. Unit tests MUST inject overlay/cwd/command and MUST NOT call GitHub.

#### Scenario: checkout -b card-* on canonical source is denied
- **WHEN** `beforeShellExecution` stdin `command` is `git checkout -b card-801-t14-qa-closeout` and `cwd` is overlay `environments.dev.source`
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` names reason `canonical_card_branch`

#### Scenario: switch -c card-* on canonical source is denied
- **WHEN** `beforeShellExecution` stdin `command` is `git switch -c card-792-x` and `cwd` is overlay `environments.dev.source`
- **THEN** the Guard returns `permission: deny`

#### Scenario: checkout -b card-* in a card worktree is not denied by this rule
- **WHEN** `beforeShellExecution` stdin `command` is `git checkout -b card-801-t14-qa-closeout` and `cwd` is a worktree path that is not `environments.dev.source`
- **THEN** this rule MUST NOT return `permission: deny`

#### Scenario: checkout of an existing branch on canonical source is not denied by this rule
- **WHEN** `beforeShellExecution` stdin `command` is `git checkout develop` and `cwd` is overlay `environments.dev.source`
- **THEN** this rule MUST NOT return `permission: deny`

### Requirement: Grok PreToolUse Guard command is cwd-independent
The Grok write-block Guard SHALL remain the compiled `decide()` adapter invoked by `.grok/hooks/process-fsm-guard.sh` (thin wrapper onto the Cursor Guard script). The `PreToolUse` command strings in `.grok/hooks/process-fsm.json` MUST locate that script with the same repo-relative + sibling + git-toplevel chain used for PostToolUse: `.grok/hooks/process-fsm-guard.sh`, then `./process-fsm-guard.sh`, then `$root/.grok/hooks/process-fsm-guard.sh` where `$root` is `git rev-parse --show-toplevel`. Running that command with cwd at the repo root, at `.grok/hooks/`, or at `frontend/` MUST exit 0 and MUST NOT exit 127 `not found`. SessionStart MUST use the same locator class for `.grok/hooks/process-fsm-session-start.sh` so the Moore page write is not muted when cwd is the repo root. This requirement MUST NOT change `scripts/process-fsm/guard.py` `decide()`, envelopes, fail-closed product writes, Cursor Guard commands, or the dsh Guard plugin. Dual-write of T0–T17 remains forbidden.

#### Scenario: Grok PreToolUse finds the Guard from three cwds
- **WHEN** a Grok `PreToolUse` command from `.grok/hooks/process-fsm.json` runs via `sh -c` with cwd at the repo root, at `.grok/hooks/`, and at `frontend/`
- **THEN** each invocation exits 0
- **AND** none exits 127 because `./process-fsm-guard.sh` was not in the cwd

#### Scenario: Grok SessionStart finds the paging adapter from three cwds
- **WHEN** the Grok `SessionStart` command from `.grok/hooks/process-fsm.json` runs via `sh -c` with those same three cwds
- **THEN** each invocation exits 0

#### Scenario: decide() and Cursor/dsh Guards stay out of this card
- **WHEN** a reviewer inspects the diff of this change
- **THEN** `scripts/process-fsm/guard.py` is not required to change for the locator
- **AND** `.cursor/hooks.json` `preToolUse` / `beforeShellExecution` remain `.cursor/hooks/process-fsm-guard.sh`
- **AND** `.dsh/plugin/process-fsm-guard.js` is not required to change for this locator

### Requirement: Guard normalizes the dsh native dialect
`scripts/process-fsm/` SHALL normalize hook stdin so `decide()` is client-agnostic across four dialects. In addition to Cursor, Grok, and OpenCode, the normalizer MUST accept the native dsh payload `{ tool, args }` whose write path key is `file_path` and whose shell key is `command`. Canonical dsh write tools SHALL include `write` and `edit`. Canonical dsh shell tool SHALL include `bash`. A dsh `edit`/`write` of a `product_globs` path with `q_git=develop` MUST take the same `write_produto` path as a Cursor `Write`. Unknown tools remain class #611: allow.

#### Scenario: dsh write of product on develop is denied
- **WHEN** stdin is a native dsh envelope `{ "tool": "write", "args": { "file_path": "backend/app/tasks/discovery_tasks.py" } }` and `q_git=develop`
- **THEN** the Guard returns `permission: deny` and `decision: deny`

#### Scenario: Four dialects deny the same product path
- **WHEN** Cursor `Write`, Grok `write` (`file_path`), OpenCode `edit` (`filePath`), and dsh `write` (`file_path`) target the same overlay product path with `q_git=develop`
- **THEN** all four return `permission: deny` and `decision: deny`

### Requirement: Authoritative GraphQL quota comes from GraphQL response headers
`scripts/process-fsm/` SHALL parse GraphQL remaining/reset from the GraphQL HTTP response: headers `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `X-RateLimit-Resource` (when Resource is present it MUST be `graphql`), plus JSON `errors[].type == RATE_LIMIT` even when HTTP status is 200. When the query succeeds and headers are absent, the parser MAY use `data.rateLimit.remaining` / `data.rateLimit.resetAt`. `X-RateLimit-Reset` MUST accept a Unix epoch or an ISO-8601 `Z` timestamp. REST `GET /rate_limit` `.resources.graphql.remaining` (including remaining=5000) MUST NOT authorize GraphQL and MUST NOT be written to the GraphQL quota cache. Unit tests MUST inject headers/body fixtures and MUST NOT call GitHub.

#### Scenario: HTTP 200 RATE_LIMIT with headers remaining 0
- **WHEN** a GraphQL response has HTTP 200, JSON `errors[0].type=RATE_LIMIT`, `X-RateLimit-Remaining: 0`, and `X-RateLimit-Reset` set
- **THEN** the parser reports remaining=0 and that reset time
- **AND** it MUST NOT treat the call as a successful Status read

#### Scenario: REST remaining 5000 does not authorize GraphQL
- **WHEN** REST `GET /rate_limit` reports `resources.graphql.remaining=5000` and GraphQL headers report remaining=0
- **THEN** GraphQL is refused
- **AND** the REST remaining MUST NOT be stored as the authoritative GraphQL quota

#### Scenario: Successful query may use rateLimit field
- **WHEN** a GraphQL query succeeds and headers are absent and `data.rateLimit.remaining` is present
- **THEN** that remaining is the authoritative GraphQL remaining for that response

### Requirement: github_status_provider is pontual and fail-immediate on GraphQL quota
`github_status_provider` SHALL query Project 1 Status for issue N with a pontual GraphQL issue→`projectItems` lookup. It MUST NOT list the whole board (`gh project item-list`) to operate one card. When GraphQL remaining is 0 or the body is RATE_LIMIT (including HTTP 200), it MUST fail immediately with the reset time (Q1=A): MUST NOT sleep until reset, MUST NOT retry GraphQL in a loop, and MUST NOT return silent `None` as if the card were off the board. Before calling GraphQL, it MUST consult the GraphQL quota cache: if remaining=0 and now is before `reset_at`, it MUST NOT call the network and MUST fail immediately with the cached reset. After a GraphQL response, it MUST update the cache from headers. Pytest MUST inject the cache path and provider fixtures and MUST NOT call GitHub.

#### Scenario: RATE_LIMIT is not silent None
- **WHEN** `github_status_provider` receives HTTP 200 with `errors[0].type=RATE_LIMIT` and headers remaining=0
- **THEN** it fails immediately with the reset time
- **AND** it MUST NOT return `None` as a missing Status

#### Scenario: Cache skip until reset
- **WHEN** the cache has remaining=0 and `now < reset_at`
- **THEN** `github_status_provider` does not call GraphQL
- **AND** it fails immediately with that reset time

#### Scenario: Pontual Status never lists the board
- **WHEN** the harness reads Status of bound card N
- **THEN** it queries only that issue's project items
- **AND** it MUST NOT call `gh project item-list` to find the column

