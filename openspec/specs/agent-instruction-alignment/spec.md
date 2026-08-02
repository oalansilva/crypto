# agent-instruction-alignment Specification

## Purpose
TBD - created by archiving change align-agent-instructions-workflow-db. Update Purpose after archive.
## Requirements
### Requirement: Agent instructions MUST reflect the workflow DB runtime model
The system MUST define agent behavior consistently with the workflow DB as runtime source of truth.

#### Scenario: Kanban as main operating surface
- **WHEN** an agent needs workflow status or handoff context
- **THEN** the instructions MUST direct the agent to use Kanban / workflow DB as the primary operational source

#### Scenario: OpenSpec remains artifact layer
- **WHEN** an agent needs proposal/design/spec/task artifacts
- **THEN** the instructions MUST describe OpenSpec as artifact/documentation storage, not the runtime workflow source

### Requirement: Agent instructions MUST reflect typed work items and parallel work rules
The system MUST define agent behavior for `change`, `story`, and `bug` work items and for parallel execution.

#### Scenario: Story and bug semantics
- **WHEN** agents work on a story with child bugs
- **THEN** instructions MUST state that child bugs block final story completion

#### Scenario: Parallel work
- **WHEN** multiple stories or agents are active
- **THEN** instructions MUST state that parallel work is allowed only under explicit locks/dependencies/WIP rules


### Requirement: Agents MUST use bounded native CI waiting
Agent instructions MUST require one owner and one native watcher for all reported pending pull-request checks, with an explicit timeout and no hand-written polling loop. The watcher MUST NOT limit observation to branch-protection-required checks because every started check needs a terminal result.

#### Scenario: Required checks are still running
- **WHEN** an agent must wait for required pull-request checks
- **THEN** it uses a native unfiltered `gh pr checks --watch` command with bounded interval and timeout instead of a `for` or `while` loop with `sleep`

#### Scenario: Long wait supports background execution
- **WHEN** the expected CI wait exceeds 60 seconds and the client supports background tasks
- **THEN** the watcher runs in the background while the agent performs independent in-scope work

### Requirement: CI waiting MUST fail closed before merge
Agent instructions MUST stop the merge phase when the watcher times out, any reported check fails, or mergeability remains blocked. A manual merge attempt MUST occur only after successful terminal checks and one final mergeability query. Each observed clean state permits at most one attempt; a failed attempt requires diagnosis and a fresh complete readiness check before retry.

#### Scenario: Watcher fails or times out
- **WHEN** the native watcher returns failure or reaches its timeout
- **THEN** the agent records the blocking state and does not invoke merge

#### Scenario: Checks succeed and pull request is clean
- **WHEN** all required checks succeed and one final query reports the pull request clean and mergeable
- **THEN** the agent performs at most one authorized manual merge attempt for that observed state

### Requirement: Agent instructions MUST declare the fixed stage-model contract
Global and project-scoped instructions MUST consistently declare Sol High for Design/OpenSpec and QA, Luna Max for development, fresh read-only Luna Max for Code Review, and Luna Max for authorized release.

#### Scenario: An agent loads workflow instructions
- **WHEN** an agent prepares or executes a card stage
- **THEN** the applicable instructions expose the exact stage executor, model, effort, permissions, entry gate, and handoff expectation

### Requirement: Generated adapters MUST remain unmodified
Model-routing policy MUST live in the Codex workflow skill, project instructions, and agent profiles rather than isolated edits to generated OpenSpec or Cursor adapters.

#### Scenario: OpenSpec command ownership changes by operation
- **WHEN** `/opsx:apply`, `/opsx:verify`, sync, or archive is routed to a stage executor
- **THEN** the canonical routing skill assigns the executor without modifying an individual generated OpenSpec skill copy

### Requirement: Automatic model routing MUST be Codex-only
The project MUST claim and validate automatic stage-model routing only in Codex. Cursor and other clients MUST remain outside the implementation and test scope of this capability.

#### Scenario: Workflow documentation names supported clients
- **WHEN** the routing contract is loaded or reported
- **THEN** it identifies Codex as the sole supported execution client and does not claim unimplemented parity elsewhere

### Requirement: Instruction drift MUST be validated automatically
The repository MUST provide a reproducible contract check for exact profile models, reasoning efforts, reviewer sandbox, stage boundaries, and fail-closed language.

#### Scenario: Workflow configuration is validated
- **WHEN** focused validation runs for the routing change or a later workflow edit
- **THEN** inconsistent TOML or missing normative stage rules fail the check before delivery
