## Why

The crypto project has 3 critical technical debt items blocking daily operations: (1) 6 integration tests in test_workflow_kanban_manual_backlog.py are failing, (2) 5 stale feature branches remain in the repo after merge, and (3) frontend/test-results/ files are untracked and blocking the upstream guard. These must be resolved to unblock the team.

## What Changes

- **Fix failing workflow integration tests**: Analyze and fix (or remove) 6 failing tests in `backend/tests/integration/test_workflow_kanban_manual_backlog.py`. Tests: `test_dev_to_qa_does_not_trigger_upstream_guard`, `test_kanban_rejects_skipping_workflow_gates_with_actionable_error`, `test_kanban_exposes_functional_publish_and_homologation_readiness_states`, `test_cancel_archive_bypasses_formal_archive_gate_flow_but_preserves_history`.
- **Clean up stale feature branches**: Delete merged local and remote branches: `feature/long-change`, `feature/monitor-candles-async-ui`, `feature/remover-locked-only-tela-carteira`, `feature/repemsar-layout`, `feature/workflow-backend-enforcement`.
- **Handle test-results/**: Add `frontend/test-results/` to `.gitignore` or commit current state — do not leave files blocking upstream guard.

## Capabilities

### New Capabilities
<!-- No new capabilities — maintenance only -->

### Modified Capabilities
<!-- No requirement changes — maintenance only -->

## Impact

- Backend: Integration tests will be green (or failures documented as known issues)
- Git: Clean branch state with no stale feature branches
- Archive flow: Unblocked from test-results/ guard
