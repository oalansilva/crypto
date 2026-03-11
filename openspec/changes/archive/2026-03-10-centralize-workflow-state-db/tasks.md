## 1. PO / Discovery

- [x] 1.1 Capture the problem: workflow state is fragmented across files/comments/Kanban
- [x] 1.2 Define target direction: workflow DB becomes the operational source of truth
- [x] 1.3 Decide transition policy for `docs/coordination/*.md`
- [x] 1.4 Define migration scope for historical changes/comments
- [x] 1.5 Define work item taxonomy (`story`, `bug`, etc.) and parent-child behavior
- [x] 1.6 Define parallel execution rules (multiple active stories, locks, dependencies, WIP limits)

## 2. DEV

- [x] 2.0 Install and configure self-hosted Postgres on the VPS
- [x] 2.0.1 Define initial infra prerequisites (database name, user, password/secret handling, persistence/volume, backup approach)
- [x] 2.0.2 Install/start Postgres and validate local connectivity from the app environment
- [x] 2.0.3 Add environment/config wiring for the new workflow database
- [x] 2.0.4 Fix runtime loading of WORKFLOW_DB_ENABLED/WORKFLOW_DATABASE_URL (Settings vs os.environ) + ensure psycopg2 installed
- [x] 2.1 Create initial Postgres schema for multi-project workflow state
- [x] 2.1.1 Add typed work items (`story`, `bug`) and parent-child links
- [x] 2.1.2 Add support for multiple active stories, agent runs, locks/ownership, and dependency tracking
- [x] 2.2 Add backend APIs for changes/tasks/comments/approvals/handoffs
- [x] 2.3 Update Kanban to read from DB-backed APIs (no legacy fallback)
  - [x] Add transitional `/api/workflow/kanban/*` endpoints that mirror legacy Kanban response shapes (changes + change comments)
  - [x] Add DB-backed `/api/workflow/kanban/changes/{id}/tasks` checklist adapter (backed by workflow work-items)
  - [x] Switch KanbanPage changes/comments/tasks to use workflow endpoints only (remove fallback to `/api/coordination/*`)
- [x] 2.4 Add migration path for currently active changes into the workflow DB model
- [x] 2.5 Add sync rules between DB and OpenSpec artifacts
- [x] 2.6 Add tests for workflow state consistency

## 3. QA

- [x] 3.1 Validate Kanban reflects DB state correctly
  - QA 2026-03-10: VPS/Postgres seed + Kanban DB-backed adapters verified.
    - Postgres schema fixes applied on VPS to match models:
      - `wf_comments.id` widened to `varchar(64)` (legacy coordination comment IDs are ~45 chars)
      - added missing columns/indexes: `wf_work_items.owner_run_id`, `wf_agent_runs.change_pk`, `wf_agent_runs.status`
    - Seed: `seed_workflow_from_coordination.py --project crypto` => `inserted_changes=1`, `inserted_gate_approvals=6`, `inserted_comments=10` (9 + QA note)
    - Audit OK: `/api/workflow/audit/coordination?project_slug=crypto` => `missing_in_db=[]`, `missing_in_coordination=[]`
    - Kanban adapters OK (no 500):
      - `/api/workflow/kanban/changes?project_slug=crypto` shows column `QA` + gate statuses
      - `/api/workflow/kanban/changes/centralize-workflow-state-db/comments?project_slug=crypto` returns the migrated thread
      - `/api/workflow/kanban/changes/centralize-workflow-state-db/tasks?project_slug=crypto` returns checklist payload with `path=.../tasks.md`
- [x] 3.2 Validate agent updates keep workflow state consistent
  - QA 2026-03-10: agent-facing workflow updates remain consistent across API/rules/audit paths.
    - Ran: `.venv/bin/pytest -q backend/tests/integration/test_workflow_api.py backend/tests/integration/test_workflow_core_service.py backend/tests/integration/test_workflow_audit_coordination.py`
    - Result: `7 passed, 4 warnings`
    - Evidence covered by tests:
      - API change/task/comment/approval/handoff writes remain coherent and queryable (`test_workflow_api.py`)
      - assignment/lock/WIP/dependency/story->bug rules reject inconsistent agent updates (`test_workflow_core_service.py`)
      - audit endpoint reports drift between DB and coordination artifacts when updates diverge (`test_workflow_audit_coordination.py`)
- [x] 3.3 Validate historical/artifact links still work
  - QA 2026-03-10: OpenSpec artifacts present (`proposal.md`, `review-ptbr.md`, `specs/*`, `tasks.md`) and Kanban adapter returns `path=.../tasks.md` for navigation.
