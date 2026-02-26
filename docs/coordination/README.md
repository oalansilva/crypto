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

### Delivery workflow (must follow)

- Always follow the agreed flow: **PO → Alan approval → DEV → QA → Alan homologation → archive**.
- If a change is already open and Alan requests a **small adjustment**, **DEV may implement it within the same change**, but the rest of the flow remains mandatory (**QA validation + Alan homologation + archive**).

## Prereqs (so the Turn Scheduler works)

### Operating mode
- PO/DEV/QA work 24/7 in timeboxed turns.
- Only notify Alan when relevant (decision needed, blocked, CI failed, ready for homologation, or prod risk).
- If waiting on Alan, mark the change as `blocked: waiting Alan` and add a Next action owned by Alan.

### Additional definitions (recommended)

To keep the process predictable, define these once and follow them:

1) **Priority / ordering**
- Use P0/P1/P2 for each active change.
- Prefer **1 active change at a time** (or at most 2) to avoid context thrash.

2) **Merge policy**
- Default: merge commit (preserve history).
- Use squash only for small hotfixes when explicitly desired.

3) **Deploy policy**
- Production = `main` deployed via `./stop.sh` + `./start.sh`.
- Deploy after merge unless explicitly testing a branch.

4) **Rollback policy**
- If a change breaks production, prefer revert on `main` first, then follow up with a fix.

5) **Contract tests for endpoints**
- Any new/changed endpoint must have at least 1 backend integration test verifying status + minimal schema.

6) **UI limits (defaults)**
- UI endpoints must be bounded (timeframe+limit).
- Prefer stable defaults (e.g., candles default limit 200) and document them.

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
