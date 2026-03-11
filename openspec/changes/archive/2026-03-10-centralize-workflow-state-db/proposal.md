## Why

The current workflow state is decentralized across OpenSpec files, coordination markdown, Kanban rendering, and comment history. This creates multiple sources of truth, tracking drift, and unnecessary complexity for both humans and agents.

Alan wants a simpler and more reliable workflow model where the operational state lives in one place inside the VPS, while OpenSpec artifacts remain useful as documentation.

## What Changes

- Introduce a central workflow state database using **self-hosted Postgres on the VPS** as the operational source of truth for changes, tasks, statuses, comments, approvals, and handoffs.
- Design the system as **multi-project** from the start, so several projects can share the same workflow core.
- Support explicit work item types such as **Story/Proposal** and **Bug**, including parent-child relationships where bugs can be linked as children of a story and opened by Alan or QA/Tester.
- Support **multiple active stories in parallel** and multiple agent runs at the same time, so the workflow reflects a real team instead of a single serialized lane.
- Keep OpenSpec proposal/design/spec/tasks files as documentation artifacts, not the primary runtime state store.
- Make the Kanban read from the workflow database instead of inferring state from multiple files, and make it the primary place where Alan consults workflow state.
- Support agent-to-agent coordination through Kanban comments, including direct mentions/replies between PO, DESIGN, DEV, QA, and Alan.
- Add migration logic to move currently active changes into the new workflow DB model after implementation.
- Add synchronization rules so OpenSpec artifacts and the workflow DB remain consistent when needed.

## Capabilities

### New Capabilities
- `workflow-state-db`: centralized workflow state management for changes, statuses, comments, approvals, and agent handoffs.

### Modified Capabilities
- `kanban`: switch Kanban data source from file aggregation to workflow DB.
- `external-balances` (indirectly none for now)

## Impact

- Backend: new persistence layer and API endpoints for workflow state.
- Frontend: Kanban and coordination views reading from DB-backed APIs.
- Agent orchestration: scheduler/agents update one source of truth.
- Docs/process: OpenSpec remains as artifact layer; DB becomes runtime state layer.
