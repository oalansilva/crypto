## ADDED Requirements

### Requirement: Guard compiles yaml and resolver before product writes
`scripts/process-fsm/` SHALL expose a Guard that, given a Cursor hook stdin JSON, extracts the path from the Cursor envelope, classifies it against yaml `product_globs` / `design_globs` **before** calling `#609` `evaluate()`, and uses the #610 resolver for `(q, bound_card, q_git)`. Event `write_produto` MUST be sent to `evaluate()` only when the path matches `product_globs`. Paths outside `product_globs` MUST return `permission: allow` when `status` is readable (including OpenSpec and prototype writes in Design). The Guard MUST NOT invent transitions, MUST NOT move Project Status, and MUST NOT replace the Impeccable adapter.

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

### Requirement: Fail-closed is asymmetric
If `status`/`q` is missing, unreadable, or a Status provider times out, the Guard MUST deny `product_globs` writes and MUST allow writes whose path matches `design_globs` when the path worktree branch already matches `card-<id>-*`. Unit tests MUST inject `status` in the stdin JSON and MUST NOT call GitHub.

#### Scenario: Status unreadable, product path
- **WHEN** stdin omits `status` and the Status provider returns nothing, and the path matches `product_globs`
- **THEN** permission is `deny`

#### Scenario: Status unreadable, design path on card branch
- **WHEN** stdin omits `status` and the path is under `openspec/changes/` or `frontend/public/prototypes/` and `q_git` matches `card-<id>-*`
- **THEN** permission is `allow`

#### Scenario: Fixtures without GitHub
- **WHEN** `pytest scripts/process-fsm -q` runs
- **THEN** Guard fixtures execute from stdin-like JSON using injected `status` and fake worktrees or stubs
- **AND** no network call to GitHub is made

### Requirement: Shell writes use the same deny as Write
`.cursor/hooks.json` SHALL register `beforeShellExecution` on the same Guard adapter. That hook SHALL apply the same deny as `Write` for commands classified as mutating a `product_globs` path (shell redirection, `tee`, `sed -i`, copy/move onto a product path). Commands that only read or test product trees (`pytest`, `ruff`, `git status`) MUST be allowed. `git commit`, `git push`, and `./restart` are out of scope (card #612).

#### Scenario: Redirect onto backend
- **WHEN** `beforeShellExecution` stdin has `command` that redirects or `tee`s onto `backend/app/main.py` and I1 does not hold
- **THEN** permission is `deny`

#### Scenario: Pytest is not a write
- **WHEN** `command` is `pytest backend/ -q` (or equivalent test runner) without a mutation token
- **THEN** permission is `allow`

### Requirement: Guard does not modify product source
This change MUST NOT edit files under `backend/` or `frontend/src/`. It MUST compose with `.cursor/hooks/impeccable.sh` rather than replace it.

#### Scenario: Product trees untouched
- **WHEN** the #611 diff is reviewed
- **THEN** no file under `backend/` or `frontend/src/` is modified
- **AND** `.cursor/hooks/impeccable.sh` remains the Impeccable adapter
