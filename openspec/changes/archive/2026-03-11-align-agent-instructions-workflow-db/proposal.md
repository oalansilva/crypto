## Why

The project is moving from a file-centered workflow to a workflow-state database with Kanban as the main operational interface. Agent behavior and instructions are still partially aligned to the old model (`docs/coordination/*.md` as runtime path, serialized turns, file-first handoffs), which will create drift and confusion if not updated.

Alan wants all agents to operate consistently under the new workflow model.

## What Changes

- Review and update the instructions/prompts/docs that define how agents operate in this project.
- Align PO, DESIGN, DEV, QA, and orchestrator behavior with the new workflow-state DB model.
- Make Kanban the main consultation/handoff surface and OpenSpec the artifact/documentation layer.
- Explicitly reflect typed work items (`change`, `story`, `bug`), parent-child rules, and parallel work rules.

## Capabilities

### New Capabilities
- `agent-instruction-alignment`: aligned agent behavior for the new workflow DB model.

### Modified Capabilities
- `workflow-state-db`: agent operating rules and handoff behavior.

## Impact

- `MEMORY.md`
- workspace `AGENTS.md`
- repo `crypto/AGENTS.md`
- any agent-facing instruction files used by PO/DESIGN/DEV/QA/main
- Kanban/process expectations documented for agents
