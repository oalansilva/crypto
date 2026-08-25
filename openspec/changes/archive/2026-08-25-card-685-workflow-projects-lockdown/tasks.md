## 1. DTO and GET gate

- [x] 1.1 Remove `database_url`, `workflow_database_url`, and `root_directory` from `ProjectOut` and `_project_out` in `app.routes.workflow`; keep them on `ProjectCreate` and the SQLAlchemy row
- [x] 1.2 Add `Depends(get_current_admin)` to `GET /projects`; leave `POST /projects` on `get_workflow_actor`
- [x] 1.3 Search remaining workflow serializers for those three keys on HTTP Project shapes and apply the same cut if found

## 2. Tests

- [x] 2.1 Add coverage: anonymous GET → 401 without connection strings; authenticated non-admin → 403; admin GET → 200 without the three keys. The 401/403 cases MUST NOT use a client that permanently overrides `get_current_admin` (that would hide the gate)
- [x] 2.2 Assert admin POST with URLs in the body → 200 redacted JSON and row still stores URLs
- [x] 2.3 Update `test_workflow_projects.py` (and other clients that GET `/api/workflow/projects`) to override `get_current_admin` where listing is required; drop asserts that required `workflow_database_url` on GET

## 3. Frontend

- [x] 3.1 Switch `ProjectSelector` GET to `authFetch`; keep slug/name options and existing loading/error UI

## 4. Closeout

- [x] 4.1 Run focused backend tests for workflow projects plus a frontend typecheck if the selector import changes
- [x] 4.2 Confirm no Alembic/seed change and no auth change on kanban/changes/scheduler/health
