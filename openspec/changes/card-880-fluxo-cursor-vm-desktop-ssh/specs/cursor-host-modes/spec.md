# cursor-host-modes — Delta Spec

## ADDED Requirements

### Requirement: Both Cursor host modes remain
The same Cursor client on this VM SHALL keep two host modes: (1) Agent/CLI in the VM terminal; (2) Cursor Desktop Windows + Remote SSH to this VM. Closing this change MUST NOT abandon either mode or force a single host.

#### Scenario: Neither mode is dropped
- **WHEN** this change reaches Done técnico
- **THEN** the runbook still names both modes as required hosts for each chat stage
- **AND** it does not instruct operators to use only the VM terminal or only Desktop+SSH

### Requirement: Each chat stage passes in both host modes
From grill through Design, Apply, review, QA and Done técnico in the same `#<id>` chat, each stage SHALL pass in modo terminal **and** in modo Desktop+SSH (Windows + this VM). Grilling in one mode and Applying in the other MUST NOT count as acceptance. Homologado and Release/lote stay out of that chat.

#### Scenario: Stage counted only in the mode where it ran
- **WHEN** grill runs in modo terminal and Apply is later requested in modo Desktop+SSH
- **THEN** Apply still has to pass in modo Desktop+SSH
- **AND** the terminal grill does not substitute for the Desktop Apply

#### Scenario: Homologado stays out
- **WHEN** a host-mode stage is proven
- **THEN** Homologado / Release / lote are not part of that proof
- **AND** `.cursor/process-fsm.yaml` gains no new event for host modes

### Requirement: Visible session root is the card folder without a hand open
After Apply starts and a `card-<id>-*` worktree already exists, the session the operator sees SHALL have that folder as the workspace root without the operator using File > Open. On modo Desktop+SSH Windows to this VM the parent MUST NOT call MCP `move_agent_to_root`. The parent SHALL bind the visible root by opening a new Remote-SSH window at the worktree URI while the chat title stays `#<id>` (not `#<id> Apply`). Isolated children MUST receive `working_directory` equal to that worktree; that cwd alone MUST NOT satisfy this requirement if the visible root is still the canonical `develop` source.

#### Scenario: Desktop plus SSH does not call move_agent_to_root
- **WHEN** the parent is in modo Desktop+SSH on Windows to this VM and needs the card folder as visible root
- **THEN** it does not call `move_agent_to_root`
- **AND** it binds a new Remote-SSH window to the worktree path
- **AND** the operator does not File > Open the folder by hand

#### Scenario: Cwd without visible root is not Q2
- **WHEN** Shell `working_directory` or `git -C` points at the worktree while the Desktop explorer root remains `environments.dev.source`
- **THEN** that stage MUST NOT be counted as continuing in the card folder
- **AND** the parent MUST bind the visible root before spawning the post-T1 activity child

#### Scenario: Terminal mode may use move_agent_to_root
- **WHEN** the parent is in modo terminal already able to change visible root without disposing InstantiationService
- **THEN** it MAY call `move_agent_to_root` or start the CLI with cwd already at the worktree
- **AND** an isolated child still MUST NOT call `move_agent_to_root`

### Requirement: Flow command finishes in the same turn without an extra click
On modo Desktop+SSH Windows to this VM, a flow command (git of the runbook, `process_event`, pytest of the harness) in a `card-<id>-*` worktree SHALL complete in the same turn without an extra operator click. The first Shell of that turn MUST request `required_permissions: ["all"]` (or the host equivalent that skips Landlock/`uid_map`). Starting with isolation `workspace_readwrite` and then asking the operator to click MUST NOT count as success. A Landlock/`uid_map` failure MUST remain visible; the screen MUST NOT go blank without an explanation.

#### Scenario: First Shell in the worktree asks for all
- **WHEN** the parent or child runs a flow command in the card worktree on this Desktop+SSH pair
- **THEN** that Shell includes `required_permissions: ["all"]` on the first attempt
- **AND** the operator is not shown an extra approval click to make the command pass

#### Scenario: workspace_readwrite first is a fail
- **WHEN** the same flow command is started with isolation `workspace_readwrite` and Landlock cannot write `/proc/self/uid_map`
- **THEN** that attempt is not a passing flow command
- **AND** retry-after-click is not the contract

### Requirement: Stage child reaches completed; host kill is this card's fail
A grill, Design-author, Apply, review, or QA child SHALL reach host status `completed` in the mode where it was spawned. A host teardown mid-work (InstantiationService disposed, window reload, SSH drop, or `Task was interrupted by the user` without a visible operator Stop in that turn) SHALL be a failure of this change. The parent MUST NOT execute the stage on Desktop as a substitute. The operator MUST NOT resume a dead child as success. An explicit operator Stop is an abort: not success, and not a host-kill of this card; the stage needs a new spawn, not resume of the corpse. Destape of a mute parent after the child already completed remains #879. Hang of the host (#879 S2) remains #879.

#### Scenario: Interrupted without visible Stop is host kill
- **WHEN** a stage child returns `Task was interrupted by the user` and the operator did not click Stop in that turn
- **THEN** the parent MUST NOT mark the stage done
- **AND** it MUST NOT continue the stage in its own Desktop transcript

#### Scenario: Operator Stop is abort not resume
- **WHEN** the operator clicks Stop on a running child
- **THEN** that child is not success
- **AND** the parent MUST spawn a new child for the stage instead of resuming the interrupted task as the passing child

### Requirement: Live proof of the broken pair plus essay for the rest
QA of this change SHALL include live proof on Windows Desktop + SSH to this VM of: visible card folder, a flow command completing in the same turn without an extra click, and a stage child reaching `completed`. Grill, Design, review, and QA SHALL have written acceptance met by essay (pytest needles, payload goldens, or rubric) without repeating a whole live card and without runbook-only evidence. Another PC (Mac, Linux, or other Windows) MUST NOT be acceptance of this change.

#### Scenario: Live proof is the three sites that broke
- **WHEN** QA asks for proof of pasta + comando + filho
- **THEN** evidence is from Windows + SSH to this VM
- **AND** a whole-card Desktop replay is not required

#### Scenario: Other Desktop pairs are out
- **WHEN** Desktop+SSH fails on a machine that is not this Windows + this VM
- **THEN** that failure is not acceptance of this change

### Requirement: Other clients stay out without the same host bug
Grok, OpenCode, and dsh SHALL stay out of this change unless Design proves the same hosting bug (InstantiationService on visible-root move, or Landlock/`uid_map` extra click) on that client. A cwd-independent hook locator (#822) MUST NOT be treated as proof of that bug.

#### Scenario: No InstantiationService on Grok means out
- **WHEN** Design records InstantiationService and Landlock/`uid_map` only on Cursor Desktop/Shell
- **THEN** Apply MUST NOT edit Grok, OpenCode, or dsh skins for this change
- **AND** it MUST NOT dual-write law into `.dsh/` or `.grok/`
