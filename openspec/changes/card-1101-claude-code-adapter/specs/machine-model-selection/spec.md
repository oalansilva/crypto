## MODIFIED Requirements

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
