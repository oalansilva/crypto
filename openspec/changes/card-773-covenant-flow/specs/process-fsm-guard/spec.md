## MODIFIED Requirements

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

## ADDED Requirements

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
