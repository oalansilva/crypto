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

- Always follow the agreed flow: **PO → DESIGN (when UI is involved) → Alan approval → DEV → QA → Alan homologation → archive**.
- If a change is already open and Alan requests a **small adjustment**, **DEV may implement it within the same change**, but the rest of the flow remains mandatory (**QA validation + Alan homologation + archive**).

### Autonomy & turn-based execution

- Default mode is **autonomous**: let the **Turn Scheduler** pull work without Alan needing to be online.
- Default to **one work item per turn** (do not do DEV+QA back-to-back in the same manual block).
- Only run multiple stages back-to-back if Alan explicitly says **"modo rápido"**.
- Pull policy: prefer finishing work **right-to-left** on the Kanban (items closest to Archived first) before starting new work.

### Communication policy (Alan)

- Send **daily-style** summaries only (no technical details like commits/files) unless Alan asks.
- Always include the **next step** and whether **Alan action is needed**.
- Do **not** send repeated updates for the same unchanged blocked state; re-notify only when the state changes or on explicit request.

### Agent-to-agent communication (Scrum-like, auditable)

- PO/DEV/QA may communicate asynchronously **via Kanban card comments** (single place, auditable).
- Use comments for handoffs, questions, decisions, and blockers.
- This does **not** change gate order: **PO → Alan approval → DEV → QA → Alan homologation → archive**.

### Update policy (reduce noise)

- **No per-turn daily spam in Telegram.**
- Each turn: the acting agent should leave a short note in the Kanban card comments (1–3 lines: what changed, blocker, next step).
- Mentions in comments: use `@PO`, `@DEV`, `@QA`, `@Alan`. Agents should respond to mentions addressed to them on their next turn (best-effort, concise).
- Each agent turn should also scan the card comments for unanswered mentions to them and reply (best-effort).
- Telegram notifications to Alan only on milestones:
  - PO ready for Alan approval
  - DEV ready for QA
  - QA ready for Alan homologation
  - Any real blocker needing Alan action

### Archiving rule (keep Kanban + OpenSpec in sync)

- When Alan says **"ok pode arquivar"**, validate the flow and close coordination first:
  - Ensure gates are satisfied in `docs/coordination/<change>.md`: PO/DEV/QA done, Alan approval approved.
  - Ensure `openspec/changes/<change>/tasks.md` has **no unchecked** items.
  - Then set `Alan homologation: approved` and add a `## Closed` section.
- Only after that, run `openspec archive ...`.
- Helper script (recommended): `scripts/archive_change_safe.sh <change>`

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
