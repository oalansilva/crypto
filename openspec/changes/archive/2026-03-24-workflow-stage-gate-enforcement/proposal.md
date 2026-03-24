# Proposal — workflow-stage-gate-enforcement

## Why

Currently, workflow cards can skip stages (e.g., move from Pending directly to DEV) without proper agent handoff. This bypasses the designed workflow gates and creates inconsistencies.

## What Changes

Implement backend enforcement to prevent stage skipping:

1. **Stage Transition Validation**:
   - When transitioning a card to a new stage, verify that all previous stages have been completed
   - Store "agent triggered" flags in the runtime to track work completion per stage
   - Block transitions that skip stages without proper agent invocation

2. **Agent Handoff Tracking**:
   - Add `last_agent_acted` field to work items
   - Track stage completion via explicit agent action, not just column movement
   - Require handoff comment when completing a stage

3. **API Enforcement**:
   - Validate stage transitions in the workflow API
   - Return 400 error if transition would skip stages
   - Include validation error message explaining which stage was skipped

## Impact

- Backend: workflow transition service must validate stage gates
- Runtime: work items will track agent activity per stage
- UX: users get clear error if trying to skip stages

## Acceptance Criteria

- [ ] Card cannot skip from Pending to DEV without PO/DESIGN activation
- [ ] Card cannot skip from DEV to QA without DEV completion
- [ ] Card cannot skip from QA to Homologation without QA validation
- [ ] API returns clear error message when stage skip is attempted
