# machine-model-selection Specification

## Purpose
TBD - created by archiving change card-1080-modelos-locais. Update Purpose after archive.
## Requirements
### Requirement: Machine selection is the sole operational source
The process SHALL resolve selections from `$HOME/.config/covenant-flow/model-selection.yaml` on the executing host/account, independently of repository or worktree. Schema version 1 SHALL distinguish all six clients (cursor, codex, grok, opencode, dsh, claude) and juizo/execucao. Rules, roles, forbidden models and capability translations SHALL remain versioned. Operational edits SHALL require no card, commit or release after initial process migration. Repository overrides, picker inheritance and fallback to the old Git map MUST NOT occur.

#### Scenario: Shared choice across consumers
- **WHEN** the operator changes Codex juizo locally and spawns from two migrated repositories and worktrees on that account
- **THEN** both new agents receive that selection explicitly, and every other client/band keeps its configured selection without any Git mutation

#### Scenario: Configuration invalid or absent
- **WHEN** the file, selected client/band, required parameter or compatible schema is missing or invalid
- **THEN** spawn fails visibly with path/client/band/reason and no substituted selection

#### Scenario: Claude entry is independent
- **WHEN** the operator edits `clients.claude.execucao` locally
- **THEN** the next Claude Code execução spawn uses the new pair and the selections of the other five clients are unchanged

### Requirement: Capabilities govern explicit routing for every harness
Cursor, Codex, Grok Build, OpenCode, dsh and Claude Code SHALL each route configured models explicitly through a supported native path. Effort or variant SHALL be supplied only when supported and required when the selected contract requires it. Capabilities SHALL come from the host schema/catalogue or tested adapter contract, not user assertions. Unsupported selections or unavailable routing SHALL fail visibly before creating an incorrectly configured child. Host/provider rejection MUST NOT trigger another model. A denied path MUST NOT be reported as proven successful coverage.

#### Scenario: Cursor model-only route
- **WHEN** Cursor spawns either named Task or generalPurpose
- **THEN** model is explicit and no unsupported effort argument is invented

#### Scenario: Codex paired route
- **WHEN** Codex spawns a juizo or execucao Agent
- **THEN** model and reasoning_effort match the selected band, including the initial Astra/medium and Sol/high choices

#### Scenario: Grok effort capability
- **WHEN** Grok accepts model but lacks a separately configurable effort field
- **THEN** model is explicit, fixed host behavior is documented, and an attempted configurable effort is rejected rather than silently ignored

#### Scenario: dsh native selection
- **WHEN** dsh supports and enables its provider/model/reasoning_effort selection contract
- **THEN** all supported selected values are passed explicitly and captured on the child without inheritance or high fallback

#### Scenario: OpenCode selection
- **WHEN** OpenCode provides a native child-session route preserving task restrictions and return semantics
- **THEN** that route receives explicit providerID/modelID and supported variant; otherwise the adapter refuses visibly and coverage stays pending

#### Scenario: Claude Code paired route
- **WHEN** Claude Code spawns a juizo or execucao subagent
- **THEN** the `Agent` call carries the native encoding of the captured model and the captured effort, initially Opus 5.5/high and Sonnet 5.5/high
- **AND** a host without per-invocation effort, or an environment override of subagent model or effort, is refused visibly before the child is created
- **AND** a call without explicit `model` and `effort` is refused rather than left to the host's default effort

### Requirement: Captures preserve running agents and coherent waves
Every new spawn SHALL reread configuration and capture immutable requested parameters, client, band, policy/capability version and source digest. Guards SHALL validate the role's band. Continuation, proxies and audits SHALL compare against that capture rather than a subsequently edited file. Reviewer/A-B waves SHALL reread before each child and reject a partial wave if that band's effective choice changes; unrelated changes SHALL NOT invalidate it. Existing agents SHALL NOT change models. Author and later critic MAY have different choices when a local edit intervenes, while both remain juizo.

#### Scenario: Editing during an agent run
- **WHEN** selection changes while a child runs or before its proxy is recorded
- **THEN** that child and its proxy retain the original capture, while the next independent spawn uses the new choice

#### Scenario: Editing between reviewers
- **WHEN** execution selection changes after the first reviewer is born and before the second
- **THEN** the wave reports selection_changed and cannot pass as a mixed wave; a new wave must be explicitly started

### Requirement: Migration preserves choices without pin side effects
Explicit migration SHALL preserve Cursor/Grok choices and initialize Codex juizo to gpt-6-astra/medium and execucao to gpt-6.1-sol/high for this requested migration. OpenCode/dsh inherited routes SHALL be materialized from their existing effective non-secret configuration, never guessed. Existing local selections SHALL NOT be silently overwritten, completed or normalized. Pins SHALL install rules/resolvers/adapters without writing selections or requiring legacy Git pairs. Unknown routes and conflicting sources SHALL produce visible incomplete migration.

#### Scenario: Existing local configuration during pin
- **WHEN** a consumer receives a new process pin
- **THEN** its machine selection bytes remain unchanged and no default pairs are injected

#### Scenario: Missing inherited route
- **WHEN** migration cannot identify a dsh or OpenCode effective route
- **THEN** that client remains explicitly unmigrated and no Cursor/Codex/Grok choice is substituted

### Requirement: Requested and observed evidence remain distinct
Evidence SHALL record requested capture separately from runtime-observed model/effort, real host/version, status and payload. Unsupported effort SHALL be not_applicable; applicable but unobserved values SHALL be unavailable. Missing trace MUST NOT be inferred from configuration and SHALL continue failing gates requiring runtime proof. This feature SHALL NOT implement missing trace support.

#### Scenario: Payload returned without model trace
- **WHEN** a child returns completed and payload but runtime does not expose its model/effort
- **THEN** observed remains unavailable and evidence does not claim verified runtime execution

