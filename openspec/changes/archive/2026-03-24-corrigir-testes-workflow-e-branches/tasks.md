## 1. Fix failing workflow integration tests

- [ ] 1.1 Run `cd /root/.openclaw/workspace/crypto && ./backend/.venv/bin/python -m pytest -q backend/tests/integration` to identify failing tests
- [ ] 1.2 Analyze each failing test in `backend/tests/integration/test_workflow_kanban_manual_backlog.py`: `test_dev_to_qa_does_not_trigger_upstream_guard`, `test_kanban_rejects_skipping_workflow_gates_with_actionable_error`, `test_kanban_exposes_functional_publish_and_homologation_readiness_states`, `test_cancel_archive_bypasses_formal_archive_gate_flow_but_preserves_history`
- [ ] 1.3 Fix or remove each failing test (fix preferred; remove only if test is obsolete)
- [ ] 1.4 Verify `pytest backend/tests/integration` passes or document failures as known issues

## 2. Clean up stale feature branches

- [ ] 2.1 Run `git branch -a` to list all local and remote branches
- [ ] 2.2 Delete local stale branches: `git branch -d feature/long-change`, `git branch -d feature/monitor-candles-async-ui`, `git branch -d feature/remover-locked-only-tela-carteira`, `git branch -d feature/repemsar-layout`, `git branch -d feature/workflow-backend-enforcement`
- [ ] 2.3 Delete remote stale branches: `git push origin --delete feature/long-change`, `git push origin --delete feature/monitor-candles-async-ui`, `git push origin --delete feature/remover-locked-only-tela-carteira`, `git push origin --delete feature/repemsar-layout`, `git push origin --delete feature/workflow-backend-enforcement`

## 3. Handle test-results/

- [ ] 3.1 Check current state of `frontend/test-results/` directory
- [ ] 3.2 Add `frontend/test-results/` to `.gitignore` OR commit current state
- [ ] 3.3 Verify upstream guard is no longer blocked
