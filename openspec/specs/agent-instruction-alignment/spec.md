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

