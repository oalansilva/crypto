# Coordination / Kanban (per change)

This folder stores lightweight coordination notes for each OpenSpec change.

## Why

Chat messages are ephemeral. These notes provide a shared, versioned view of:
- current status
- decisions
- links
- next actions

## Rules

- If it matters, it must be written down here or in the OpenSpec artifacts.
- Keep each file short and actionable.
- Prefer linking to sources (PR, CI runs, OpenSpec viewer) over copying long logs.

## Prereqs (so the Turn Scheduler works)

For each active change file (`docs/coordination/<change>.md`), ensure:

- Status section is present and up to date (PO/DEV/QA/Alan).
- Decisions (locked) includes defaults + limits (especially performance limits).
- Links include:
  - OpenSpec viewer
  - PT-BR review (viewer)
  - PR
  - CI run
- Next actions contains **small, timeboxed** tasks (one role per checkbox), using:
  - `[ ] PO:` / `[ ] DEV:` / `[ ] QA:` / `[ ] Alan:`
- If waiting for Alan, mark the change as blocked and add a Next action owned by Alan.

## Template

Create one file per change:

- `docs/coordination/<change-name>.md`

Suggested structure:

```markdown
# <change-name>

## Status
- PO: (not started|in progress|blocked|done)
- DEV: (not started|in progress|blocked|done)
- QA: (not started|in progress|blocked|done)
- Stakeholder (Alan): (not reviewed|reviewed|approved)

## Decisions (locked)
- ...

## Links
- OpenSpec viewer: ...
- PT-BR review: ...
- PR: ...
- CI run: ...

## Notes
- ...

## Next actions
- [ ] PO: ...
- [ ] DEV: ...
- [ ] QA: ...
- [ ] Alan: ...
```
