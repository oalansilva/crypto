## MODIFIED Requirements

### Requirement: Guard compiles yaml and resolver before product writes
`scripts/process-fsm/` SHALL expose a Guard that, given a Cursor hook stdin JSON, extracts the path from the Cursor envelope, classifies it against yaml `product_globs` / `design_globs` **before** calling `evaluate()`, and uses the resolver for `(q, bound_card, q_git)`. Event `write_produto` MUST be sent to `evaluate()` only when the path matches `product_globs`. Paths outside `product_globs` MUST return `permission: allow` when `status` is readable (including OpenSpec and prototype writes in Design), **except** (a) Shell commands classified as Project Status edits and (b) any `Write`/`StrReplace`/`Delete` whose path ends with `.design-digest`, or Shell classified as **mutating** a `.design-digest` path (any `q`; classified **before** `design_globs` glob-first). Exception (b) MUST NOT fire solely because the substring `.design-digest` appears in a non-mutating Shell command (including `git add`, `git commit`, `git status`, or `git reset` that only cite the filename). The Guard MUST NOT invent transitions, MUST NOT move Project Status, and MUST NOT replace the Impeccable adapter.

Fixtures MUST use the live Cursor envelope, not an internal dict that skips the parser:
- `preToolUse`: `tool_name`, `tool_input` (`path` / `file_path` / `file` / `target_notebook`), `cwd`; tests MAY inject `status`.
- `beforeShellExecution`: `command`, `cwd`; tests MAY inject `status`.

#### Scenario: Product write allowed under I1
- **WHEN** stdin JSON is a `Write` (or `StrReplace`/`Delete`/`EditNotebook`) of a `product_globs` path, `status` is `Em desenvolvimento` or `Code Review`, `q_git` is `card-<id>-*`, and `bound_card` equals that id
- **THEN** the Guard returns `permission: allow`

#### Scenario: Illegal product write is denied
- **WHEN** stdin JSON is a product `Write` and any of Todo, Design, Aprovação de Design, Pronto para Dev, QA, Done, Homologado, Pronto, Cancelado, `q_git=develop`, `q_git=main`, or `bound_card=⊥` holds
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` names the reason (`I1`, `I3`, illegal_edge id, or unbound)

#### Scenario: I3 two-phase apply
- **WHEN** `status` is `Pronto para Dev` and the tool writes a `product_globs` path even with `q_git=card-<id>-*` and matching `bound_card`
- **THEN** the Guard returns `permission: deny`
- **AND** allow happens only after `status` is already `Em desenvolvimento`

#### Scenario: Replay b6a71170
- **WHEN** the fixture is `Write` of `backend/app/tasks/discovery_tasks.py` with `q_git=develop`
- **THEN** the Guard returns `permission: deny`

#### Scenario: Design OpenSpec write is not write_produto
- **WHEN** stdin is `preToolUse` `Write` of a path under `openspec/changes/` (or `frontend/public/prototypes/`) and `status` is `Design` and `q_git` matches `card-<id>-*`
- **THEN** the Guard returns `permission: allow`
- **AND** `evaluate(write_produto)` is not invoked for that path
- **AND** the path does not end with `.design-digest`

#### Scenario: Sidecar write is denied even under design_globs
- **WHEN** stdin is `preToolUse` `Write` (or `StrReplace`/`Delete`) of `openspec/changes/<change>/.design-digest` with a file path present and `status` is `Design` (or any other `q`)
- **THEN** the Guard returns `permission: deny`
- **AND** it MUST classify the sidecar **before** the `design_globs` allow

#### Scenario: Git cite of sidecar is not denied by substring
- **WHEN** `beforeShellExecution` stdin `command` is `git add`, `git commit`, `git status`, or `git reset` that mentions `.design-digest` only as a path or message cite (no write/redirect/`rm`/python open-write of the sidecar)
- **THEN** the Guard MUST NOT return `permission: deny` for reason `sidecar`

### Requirement: Guard denies Agent Status item-edit
The Guard `beforeShellExecution` **and** `preToolUse` paths SHALL classify `.design-digest` **mutations** and Status board edits **before** the missing-path early-return and **before** `design_globs` glob-first allow. It SHALL deny a Cursor Shell command that edits Project 1 `Status` via `gh project item-edit` (Status field id `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM`, or a `--single-select-option-id` that is a Status option) or via GraphQL `updateProjectV2ItemFieldValue` targeting that field, **even when** the same `command` string also contains `process_event.py`. A Shell command that is **only** a python invocation of `scripts/process-fsm/process_event.py` plus a named event and flags MUST be allowed by this Status-edit rule. The Guard MUST deny `Write`/`StrReplace`/`Delete` whose path ends with `.design-digest`. The Guard MUST deny Shell classified as mutating a `.design-digest` path (redirect/`tee` onto the sidecar, `rm`/`unlink` of the sidecar, `cp`/`mv`/`install` with sidecar destination, `sed -i`/`perl -i` on the sidecar, or `python`/`python3 -c` that opens/writes the sidecar). The Guard MUST NOT deny Shell solely because `.design-digest` appears as a substring without such mutation (including git cite). The bash fallback in `.cursor/hooks/process-fsm-guard.sh` MUST apply the same Status-edit and sidecar-mutation denies before allowing commands that have no file path and before any `design_globs` allow. The Guard MUST NOT honor `PROCESS_FSM_MOVE` or any environment allow. The Guard MUST still NOT itself move Project Status. `git commit`, `git push`, and `./restart` remain out of scope as product-write hooks (they MUST still not be denied merely for citing `.design-digest`).

#### Scenario: Direct item-edit of Status is denied
- **WHEN** `beforeShellExecution` stdin `command` contains `gh project item-edit` and the Status field id, even if no file `path` is present
- **THEN** the Guard returns `permission: deny`
- **AND** it MUST NOT take the missing-path early-return allow
- **AND** `agent_message` tells the Agent to use `process_event`

#### Scenario: process_event CLI is allowed
- **WHEN** `command` is solely a python invocation of `scripts/process-fsm/process_event.py` with a named event and optional flags (no `item-edit` / GraphQL Status in the same string)
- **THEN** this Status-edit rule does not deny the command

#### Scenario: Chained process_event and item-edit is denied
- **WHEN** `command` contains both `process_event.py` and `gh project item-edit` with the Status field id
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
