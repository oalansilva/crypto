## Context

Today the workflow uses several state carriers at once:
- OpenSpec change files
- `docs/coordination/<change>.md`
- Kanban UI aggregation
- comments/daily notes

This creates drift, forces manual reconciliation, and makes agent automation fragile.

## Goals / Non-Goals

**Goals**
- Create one operational source of truth for workflow state.
- Preserve OpenSpec as documentation/artifact storage.
- Reduce tracking inconsistencies between tasks, coordination, and Kanban.
- Make agent orchestration easier and cheaper by giving agents a single place to read/write workflow state.

**Non-Goals**
- Replacing OpenSpec as a documentation format.
- Rebuilding the entire app UI in this change.
- Migrating every historical detail at once.

## Proposed Architecture

### Source of truth
Use a **self-hosted Postgres** database on the VPS as the workflow core, with multi-project support from day one.

Business rules:
- A `story` can only be completed when all of its child `bug` work items are completed. Child bugs are prerequisites for closing the parent story.
- Multiple stories may be active at the same time.
- Multiple agent runs may execute in parallel, provided the system tracks ownership/locks and explicit dependencies.

Suggested core tables:
- `projects`
- `changes`
- `work_items` (with `type`, e.g. `story`, `bug`)
- `work_item_links` (parent-child relationships)
- `tasks`
- `comments`
- `approvals`
- `handoffs`
- `artifacts`
- `status_history`
- `agent_runs`
- `project_settings`

### OpenSpec role
OpenSpec files continue to exist for:
- proposal
- design
- spec
- task artifacts

But runtime workflow state moves to the DB.

### Kanban role
Kanban reads from DB-backed endpoints instead of inferring state from multiple files.

### Sync strategy
- New changes create DB rows immediately.
- OpenSpec files are linked as artifacts.
- Agents update DB first; artifact reconciliation happens in controlled steps.

## Open Questions

1. Should markdown coordination files remain as human-readable mirrors, or be retired after migration?
2. Should comments live only in DB, or also sync back to markdown summaries?
3. How much history should be migrated from existing changes?

## Initial Recommendation

- Use **Postgres self-hosted on the VPS** as the workflow core.
- Design the schema for **multiple projects** sharing the same coordination system.
- Treat the workflow DB as authoritative from the start of this change.
- Remove `docs/coordination/*.md` from the operational runtime path.
