## Why

Currently, workflow rules (approval gates, story-bug dependencies, required comments) are defined only in markdown files (MEMORY.md, playbooks, AGENTS.md) and depend on human/LLM adherence. This leads to errors like approving without links, closing stories with open bugs, or skipping required handoffs. Enforcing these rules in the backend prevents runtime violations.

## What Changes

- Add validation layer in backend API to enforce workflow rules before state transitions
- Implement approval gate validation (require review links)
- Implement story-bug closure validation (story cannot close if bugs active)
- Implement handoff comment requirement (require status/evidence in comments)
- Add sync verification endpoint (check DB ↔ OpenSpec consistency)
- Auto-update DB state on Homologation approval
- Enforce DEV→QA→publish sequence in transition service

## Capabilities

### New Capabilities
- `workflow-validation`: Backend validation service for workflow rules
- `approval-gate-enforcement`: Validate required links before accepting approvals
- `story-bug-closure-rule`: Enforce story closure requires all bugs done
- `handoff-comment-validation`: Require structured comments on stage transitions
- `sync-verification`: Endpoint to verify DB ↔ OpenSpec consistency

### Modified Capabilities
- None (new capabilities only)

## Impact

- Backend: new validation services in `app/services/`
- API: new endpoint `/api/workflow/verify-sync`
- Workflow transitions: updated in `workflow_transition_service.py`
