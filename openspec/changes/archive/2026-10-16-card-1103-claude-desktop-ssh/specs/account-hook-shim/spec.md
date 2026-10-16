## ADDED Requirements

### Requirement: Adapter digest covers what runs and only what runs
The adapter part (A) of the trust digest SHALL cover every file the client's adapter can execute and the manifest data that decides what runs, and SHALL exclude data and fixtures that the hook never executes. Specifically: `scripts/process-fsm/route-landmarks.yaml` (R1) and `scripts/process-fsm/*_fixtures.py` (R2) SHALL be excluded from `CORE_TREES`; the client's `entrypoints`/`modules` block of the adapter manifest SHALL be part of A (R3); `enumerate_tree` SHALL follow directory symlinks and include their targets, and a symlink leaving the repository SHALL fail the pin (R4); only `__pycache__/` directories and the `.pyc` files inside them SHALL be excluded as cache, so a loose `.pyc` is part of A (R5); a listed file whose digest cannot be computed SHALL fail the pin naming the path instead of being dropped (R6); the Impeccable `detector/` tree SHALL be part of A (R7).

#### Scenario: Editing the route catalog or a fixture
- **WHEN** `route-landmarks.yaml` or `claude_fixtures.py` changes in the worktree
- **THEN** the adapter digest is unchanged and no hook returns `adapter_divergent`

#### Scenario: Changing only the executed argv
- **WHEN** only the `entrypoints` of a client in the manifest change
- **THEN** A differs from the reviewed digest and the shim refuses with `hooks_unreviewed`

#### Scenario: Module reached through a directory symlink
- **WHEN** a directory symlink inside a tracked tree points to a module that changes
- **THEN** A changes; and a symlink pointing outside the repository fails the pin visibly

#### Scenario: Loose pyc and detector change
- **WHEN** a `.pyc` outside `__pycache__/` is added or a byte changes under the Impeccable `detector/`
- **THEN** A differs from the reviewed digest

#### Scenario: Unreadable listed file
- **WHEN** the pin builds the manifest and a listed file yields no digest
- **THEN** the pin fails naming the file and writes no manifest

### Requirement: Registration digest is anchored at session startup only
The shim SHALL write the registration digest (R) in the heartbeat only on `SessionStart` with source `startup`; `compact`, `clear` and `resume` SHALL keep the recorded R, so `hooks_changed` still fires after a registration change (R8).

#### Scenario: Registration changes then the session compacts
- **WHEN** the account hook block changes and the session later compacts
- **THEN** the heartbeat keeps the startup R and dependent transitions are refused with `hooks_changed`

### Requirement: Shim decides client and consumer from what called it
The shim SHALL decide a foreign Cursor call by the client of the registration that invoked it, not by inherited `CURSOR_*` environment (R9). Cursor and OpenCode SHALL detect their client natively for the `hooks_inactive` refusal, without depending on `--client` or `COVENANT_CLIENT` (R10). Discovery SHALL climb out of a nested Git repository without overlay until it finds the pinned consumer that contains it, so the session keeps its gates (R11). A failing dynamic `import()` in the OpenCode plugin SHALL NOT block `read`; writes, shell and spawn stay denied (R12).

#### Scenario: Codex inside a Cursor terminal
- **WHEN** the Codex registration calls the shim from a process that inherited `CURSOR_*` variables
- **THEN** the shim handles it as a Codex call

#### Scenario: Cursor transition without client flag
- **WHEN** `process_event` runs in Cursor without `--client` or `COVENANT_CLIENT` and the shim heartbeat is missing
- **THEN** the transition is refused with `hooks_inactive`

#### Scenario: Nested repository inside the consumer
- **WHEN** the session cwd is a nested Git repository without overlay inside a pinned consumer
- **THEN** the consumer's adapter governs the event and product writes are judged by its Guard

#### Scenario: OpenCode plugin import fails
- **WHEN** the OpenCode plugin cannot import the pinned adapter
- **THEN** `read` is allowed and write, shell and spawn are denied with the reason

### Requirement: Only the operator records trust
`trust --record` SHALL require an interactive confirmation from the operator and SHALL refuse when run inside an agent session of any account-registered client. `shim_verified()` SHALL NOT accept `CF_SHIM_ACTIVE` or `CF_SHIM_ADAPTER_DIGEST` from the environment as proof of review; the adapter SHALL check against the account trust record (R15).

#### Scenario: Agent tries to record trust
- **WHEN** an agent session runs `cf_shim.py trust --record`
- **THEN** the command refuses and the trust record is unchanged

#### Scenario: Forged environment
- **WHEN** a process sets `CF_SHIM_ACTIVE=1` and an arbitrary `CF_SHIM_ADAPTER_DIGEST`
- **THEN** the adapter does not treat the session as reviewed

### Requirement: Page warns about mixed pins
When the worktrees a session has touched carry different pins, the page SHALL say so, naming each root and pin (R16).

#### Scenario: Session crosses two pins
- **WHEN** a session moves from a worktree on one pin to a worktree on another
- **THEN** the injected page warns about mixed pins

### Requirement: Account installer removal is lossless
`install.sh --account --remove` SHALL rewrite a host file only when it contained Covenant Flow entries, SHALL never create an empty `hooks` object nor change a file without entries (Claude Code, Codex and Cursor, R18 and R19), and SHALL remove the versioned shim directory together with the `current` link (R20). The nucleus `install.sh` diff SHALL be part of the consumer's review wave diff (R21).

#### Scenario: Remove on a settings file without entries
- **WHEN** `--remove` runs on a `settings.json` that is `{}` or has no Covenant Flow entries
- **THEN** the file is byte-identical afterwards

#### Scenario: Remove after install
- **WHEN** `--remove` runs after `--account`
- **THEN** no Covenant Flow entry, empty `hooks` object, shim directory or dangling link remains, and foreign entries are preserved
