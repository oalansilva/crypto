## ADDED Requirements

### Requirement: The desktop app over SSH is a surface of the claude client
Sessions opened by the Claude desktop app on Windows through SSH to the operator's VM SHALL run locally on the VM and SHALL be treated as the existing `claude` client, with the same FSM, Guard, model selection and evidence as the terminal. No new client value, selection block or adapter SHALL be introduced. The surface value `claude-desktop` SHALL become a known surface of the evidence collector only together with a real, sanitized transcript fixture taken from a real session of the app's own Claude Code copy, and the live rehearsal SHALL confirm it; without that fixture, the surface SHALL stay `unverified` and fail visibly. The observed surface, the host version of the app's copy and, when available, the desktop app version SHALL be recorded in the shim heartbeat, the birth receipt, the collected evidence, the proxy line and the handoff. A session whose transcript carries more than one surface SHALL be refused as `unverified`.

#### Scenario: App session recognized after rehearsal
- **WHEN** a session opened by the desktop app (`entrypoint=claude-desktop`) prepares and collects a stage child after the real fixture is recorded
- **THEN** the birth is accepted and the evidence and proxy record client `claude`, surface `claude-desktop`, the host version of the app's copy and the observed model and effort

#### Scenario: Surface not yet rehearsed
- **WHEN** the collector meets `entrypoint=claude-desktop` without the real fixture in place
- **THEN** the stage stops with `unverified`, citing the observed surface, and nothing passes to the terminal

#### Scenario: Mixed surfaces in one session
- **WHEN** a session started in the app is resumed in the terminal and its transcript carries both `claude-desktop` and `cli`
- **THEN** `prepare` and `collect` refuse the session as `unverified`

### Requirement: Host version is read from the session, never from the binary on PATH
Inside a Claude Code session, the host version used for capability floors SHALL come from the session itself (`AI_AGENT`, confirmed against the transcript `version` in `prepare`). The `claude --version` fallback SHALL only be used outside a Claude Code session. When the session version cannot be read, resolution and birth SHALL fail with `capability_unavailable` citing the surface. Capability floors SHALL be per-invocation effort at 2.1.292 and blocking hooks at 2.1.295, enforced in code, documentation and design alike.

#### Scenario: App copy differs from the terminal binary
- **WHEN** the app's copy is 2.1.295 and the terminal binary on PATH is 2.1.300
- **THEN** heartbeat, receipt and proxy record 2.1.295 and the PATH binary is never queried

#### Scenario: Session version missing
- **WHEN** a session lacks `AI_AGENT`
- **THEN** `model_selection.py resolve --client claude` and `claude_evidence.py prepare` fail with `capability_unavailable` naming the surface, without running `claude --version`

#### Scenario: Host below the blocking-hook floor
- **WHEN** the session's host version is below 2.1.295
- **THEN** births and hook-dependent transitions are refused with `capability_unavailable`

### Requirement: A folder created by the app is a folder without a card
A session opened by the desktop app in a folder the app created (the app's worktree option, by default `<project-root>/.claude/worktrees/<name>`, or the configured worktree folder) SHALL be treated as a folder without a bound card, because its branch does not match `card-<id>-*`. In it, product and OpenSpec writes SHALL be denied, stage children SHALL NOT be born and `process_event` SHALL refuse, all with a visible reason that names the folder as created by the app and gives the recovery: asking `#<id>` in the same session enters the card worktree through `EnterWorktree`. The app's folder SHALL NOT be adopted as a card worktree nor deleted by the agent. `.claude/worktrees/` SHALL be ignored by git in the consumer so the app's folders do not dirty `/source`.

#### Scenario: Session opened in the app's worktree
- **WHEN** Alan opens a session through the app with its worktree option on, inside the pinned repository
- **THEN** the first answer states that the folder was created by the app and has no card, and an attempt to edit a product file is denied with the same reason and the `#<id>` recovery

#### Scenario: Leaving the app's folder for the card worktree
- **WHEN** Alan asks `#<id>` in that session
- **THEN** the session enters `card-<id>-*` through `EnterWorktree`, the page shows `bound_card=<id>`, and the app's folder stays untouched

#### Scenario: App folder outside any pinned repository
- **WHEN** the app opens a session in a folder with no pinned consumer
- **THEN** no process hook acts there, as for any folder without a pin

### Requirement: Stage children are born only through Agent in app sessions
With a bound card, the hook SHALL deny the app's session tools that create a session, send a message to another session or open a session in another folder (the `mcp__ccd_*` family observed in the rehearsed version), with the reason that stage children are born only through `Agent` with capture and receipt. An unclassified `mcp__ccd_*` tool SHALL be treated as session-creating. Read-only and layout tools of the app SHALL stay allowed. Without a bound card these tools SHALL stay allowed.

#### Scenario: Spawning a task through the app with a bound card
- **WHEN** the parent of a bound card calls the app's spawn-task tool
- **THEN** the call is denied visibly and no session is created

#### Scenario: Listing sessions is not blocked
- **WHEN** the parent lists sessions or changes the layout through the app's tools
- **THEN** the call is allowed

### Requirement: Alan follows the card session and its children from the app
In an app session bound to a card, the session title SHALL carry `#<id>`; stage children SHALL be born with the `description` `<role> <id> <unique>` so the app's task and subagent panes show the stage of each child and its status; and at the end of each child the parent SHALL write in the chat and in the card handoff one line per child with client, surface, observed model and effort, and status, taken from the proxy and never from the request. The board SHALL remain the place where Status is seen.

#### Scenario: Opening the app on a card in progress
- **WHEN** a card is in progress and Alan opens the app
- **THEN** he sees the card session by `#<id>` and its children side by side with stage and result, without the terminal

#### Scenario: Child finishes in the app
- **WHEN** a child opened by the app session finishes
- **THEN** the handoff records client `claude`, surface `claude-desktop` and the observed model and effort
- **AND** when the evidence is missing or diverges, the gate that requires it fails and the reason appears in the app chat

### Requirement: Process guarantees in the app equal the terminal
In an app session, a request `implemente` on a card in `Todo` SHALL change no product file and the answer SHALL cite the current Status; product writes outside the stage SHALL be denied by command and by file edit; children SHALL use the band model with explicit `model` and `effort`; human gates T1, T7, T15 and T18 SHALL stay Alan's on the board. The app's permission mode (it launches in `auto`) SHALL NOT authorize any process step, and no Auto mode SHALL be claimed.

#### Scenario: implemente in Todo through the app
- **WHEN** a card is in `Todo` and Alan asks `implemente` in the app session
- **THEN** no product file changes and the answer cites the current Status, as in the terminal

#### Scenario: Deny under the app's auto permission mode
- **WHEN** the app session runs in `auto` and the agent tries to edit a product file on `develop`
- **THEN** the hook denies the edit and the file is unchanged

#### Scenario: Spawn without effort in the app
- **WHEN** the parent in the app spawns a stage child without `effort`
- **THEN** the spawn is denied with `unsupported_schema` or the missing field, and no child runs at the session effort

### Requirement: Missing protection in the app fails visibly without fallback
Where the app's copy lacks the hook registration, per-invocation effort, a readable session version, a transcript in the expected format or the required evidence, the stage SHALL stop with the reason visible in the app chat (`hooks_inactive`, `capability_unavailable`, `unsupported_schema`, `unverified`, deny reason). The agent SHALL NOT move the stage to the terminal, change model or omit effort as a way out.

#### Scenario: Registration not loaded in the app
- **WHEN** an app session has no shim heartbeat and the parent tries a dependent transition
- **THEN** `process_event` refuses with `hooks_inactive` and the recovery, and the agent does not continue in the terminal

### Requirement: Live rehearsal of a whole card through the app
Before the T14 of this change, the flow SHALL be rehearsed for real in the desktop app on Windows over SSH: the negatives of the observable criteria (`implemente` in `Todo`, product write denied, spawn without effort or with a divergent model denied, app folder refused and left through `EnterWorktree`, app session tool denied with a bound card, missing or divergent evidence failing the gate) and one real card chosen and prioritized by Alan, stacked on the QA-green SHA of this change, conducted through the app from Em Refinamento to QA green. Evidence SHALL be recorded on this change's card, one comment per block, and the rehearsal card's own evidence also on the rehearsal card: shim heartbeat with surface and versions, receipts and proxies per child, the real sanitized transcript fixture, `process_event` outputs, the deny reasons from the transcript and the session and child identifiers.

#### Scenario: Rehearsal recorded
- **WHEN** the rehearsal ends
- **THEN** the card has, per block, the session and child identifiers, the surface `claude-desktop`, the observed models equal to the captures and the deny and refusal reasons seen in the app

#### Scenario: Rehearsal step fails
- **WHEN** a step of the rehearsal does not work in the app
- **THEN** the gap is recorded on the card as a visible failure and no mechanism is invented to pass it
