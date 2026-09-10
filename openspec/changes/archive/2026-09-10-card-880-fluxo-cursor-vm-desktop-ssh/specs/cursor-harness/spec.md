## ADDED Requirements

### Requirement: Parent binds visible root; isolated child never calls move_agent_to_root
On Cursor, the **parent** SHALL bind the operator-visible workspace root to the card worktree `card-<id>-*` after that tree exists. An isolated activity child MUST NOT call MCP `move_agent_to_root`. On modo Desktop+SSH Windows to this VM the parent MUST NOT call `move_agent_to_root` either (witness 2026-09-09: `Failed to move agent root: InstantiationService has been disposed`). In that mode the parent SHALL open a new Remote-SSH window at the worktree URI with chat title `#<id>` and MUST NOT ask for `#<id> Apply`. Children SHALL still use `working_directory` equal to the worktree; that parameter MUST NOT replace a visible-root bind.

#### Scenario: Isolated child does not move agent root
- **WHEN** a grill, Design-author, Apply, review, or QA child runs
- **THEN** its prompt forbids `move_agent_to_root`
- **AND** Write/Shell in that child use the worktree path without changing the live workbench root

#### Scenario: Desktop plus SSH parent skips the broken MCP
- **WHEN** the Cursor parent on Windows Desktop + SSH to this VM needs the card folder as visible root
- **THEN** it does not call `move_agent_to_root`
- **AND** a retry of that MCP after InstantiationService disposed is also forbidden

### Requirement: Flow Shell on this Desktop plus SSH pair does not wait for an extra click
Flow commands of the Cursor runbook (git, `process_event`, harness pytest) executed in a `card-<id>-*` worktree on Windows Desktop + SSH to this VM SHALL request `required_permissions: ["all"]` on the first Shell of the turn. Isolation `workspace_readwrite` that fails Landlock/`uid_map` (`Failed to write /proc/self/uid_map`) MUST NOT be the first attempt of a passing flow command. The failure MUST stay visible; a blank workbench without explanation is not a pass. This requirement MUST NOT add a FSM event, MUST NOT grow always-on `AGENTS.md`, and MUST NOT set overlay `clients.*.auto`.

#### Scenario: All on the first attempt
- **WHEN** T8 or a later flow Shell runs in the card worktree on this Desktop+SSH pair
- **THEN** the Shell payload includes `required_permissions: ["all"]` before Landlock is tried
- **AND** the operator does not click an extra approval to finish the command

#### Scenario: No pin and no auto overlay for sandbox
- **WHEN** this change is applied
- **THEN** it does not bump overlay `pin` solely for host sandbox
- **AND** it does not write `clients.*.auto`

### Requirement: Host interrupt of a Cursor child is not success
A Cursor Task/subagent for a stage child SHALL be treated as success only when the host reports `completed` and the child return payload is present. `Task was interrupted by the user` without a visible operator Stop in that turn SHALL be classified as host kill and MUST NOT satisfy the stage. The parent MUST NOT run the stage itself on Desktop to compensate. Destape after a child already completed stays #879.

#### Scenario: Interrupted Apply child is not T8 success
- **WHEN** an Apply child ends with `Task was interrupted by the user after` a duration and the operator did not Stop
- **THEN** the parent MUST NOT treat Apply as done
- **AND** it MUST NOT implement the remaining tasks in the parent Desktop transcript
