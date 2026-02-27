## Context

We already maintain coordination state in markdown and OpenSpec artifacts. We want a visual board in the app without losing the file-based “source of truth” that automation depends on.

## Goals / Non-Goals

**Goals**
- Visual Kanban board inside the app.
- Card details view for tasks + comments.
- Keep file-based status as the source of truth.

**Non-Goals**
- Replacing OpenSpec/coordination files.
- Multi-user permissions; this is a single-operator admin UI.

## UI

- Route: `/kanban`
- Columns match our workflow:
  - PO
  - Alan approval
  - DEV
  - QA
  - Alan homologation
  - Archived (toggle)
- Card shows:
  - change name
  - current stage
  - next step (derived from coordination)
  - last update timestamp (best-effort)

## Data model

### Status source
- Parse `docs/coordination/<change>.md` for:
  - PO status
  - DEV status
  - QA status
  - Alan status

### Tasks source
- Parse `openspec/changes/<change>/tasks.md` markdown checkboxes.

### Comments store
- Store comments in a simple server-side JSONL or sqlite table keyed by change name.
- Provide endpoints:
  - `GET /api/coordination/changes` (active changes + statuses)
  - `GET /api/coordination/changes/:name/tasks`
  - `GET /api/coordination/changes/:name/comments`
  - `POST /api/coordination/changes/:name/comments`

## Risks / Trade-offs

- Markdown parsing: keep minimal parsing rules and add tests.
- Concurrency: single operator; simple append-only comments storage is fine.
