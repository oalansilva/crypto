## MODIFIED Requirements

### Requirement: Design gate is process-based
While `Status=Design`, the Cursor session SHALL author OpenSpec artifacts and a navigable prototype when UI-impacting, then spawn an isolated same-model critique Task. Isolated critics MUST NOT edit product code, `design.md`, or prototype files. They MAY write only `.impeccable/critique/**`. The agent MUST NOT implement product code until `Status=Pronto para Dev`.

#### Scenario: Isolated critique
- **WHEN** Design evidence is ready
- **THEN** Assessment uses a separate Task that MUST NOT edit product, `design.md`, or prototype files
- **AND** the Task MAY write only `.impeccable/critique/**`
- **AND** missing critique or empty snapshot keeps the verdict `BLOCKED`

#### Scenario: No OpenCode lock machine
- **WHEN** Design runs in Cursor
- **THEN** the flow MUST NOT require `design_spawn_stage`, `design_artifact_write`, lease evidence or OpenCode 1.18.18 attestation

## ADDED Requirements

### Requirement: One chat per column on both clients
The Cursor and Grok runbooks SHALL require a separate chat per column (Design, Apply, Review, Release) with title `#<issue-id> <coluna>`. The agent MUST refuse to mix those columns in one transcript. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry.

#### Scenario: Design chat refuses apply
- **WHEN** the bound card is in `Status=Design` and the current chat is the Design session
- **THEN** a request to `/opsx:apply` or implement product code in that same transcript is refused
- **AND** the agent asks for a new chat titled `#<id> Apply` after `Pronto para Dev`

#### Scenario: Both clients carry the same refusal
- **WHEN** `alan-workflow` is followed in Cursor or via the Grok stub
- **THEN** both clients document `#id coluna` and the mix refusal
- **AND** `.cursor/process-fsm.yaml` has no new event for this rule

### Requirement: Apply does not ingest the whole OpenSpec dump
`.cursor/skills/openspec-apply-change/SKILL.md` SHALL instruct the agent, for each pending task, to read that task, the matching capability spec, and the short apply sections of `design.md`. It MUST NOT instruct the agent to read every `contextFiles` path as a single dump. It MUST NOT instruct reading `.impeccable/critique/`. For `UI impact: affected`, the skill still requires reading the prototype file on disk before product UI edits.

#### Scenario: Apply skill no longer dumps every context file
- **WHEN** `/opsx:apply` starts a task
- **THEN** the skill tells the agent to load the current task, the matching spec, and short `design.md` apply sections
- **AND** the skill does not say to read every `contextFiles` path before starting
