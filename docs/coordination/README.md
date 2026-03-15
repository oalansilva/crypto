# Coordination / Kanban (per change)

This folder stores lightweight coordination notes for each OpenSpec change.

## Why

Chat messages are ephemeral. These notes provide a shared, versioned view of:
- current status
- decisions
- links
- next actions

## Rules

- If it matters, it must be written down in runtime/Kanban or the OpenSpec artifacts; coordination markdown mirrors the result for audit/readability.
- Keep each file short and actionable.
- Prefer linking to sources (PR, CI runs, OpenSpec viewer) over copying long logs.
- `docs/coordination/*.md` is not the live operational source for active work; workflow DB + Kanban comments/work items are.
- For the standardized role contract, handoff template, and Definition of Done by stage, follow `docs/multiagent-operating-playbook.md`.

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
- Use comments for handoffs, questions, decisions, blockers, ownership clarifications, and dependency notes.
- This does **not** change gate order: **PO → Alan approval → DEV → QA → Alan homologation → archive**.

### Update policy (reduce noise)

- **No per-turn daily spam in Telegram.**
- Each turn: the acting agent should leave a short note in the Kanban card comments (1–3 lines: what changed, blocker, next step).
- Mentions in comments: use `@PO`, `@DESIGN`, `@DEV`, `@QA`, `@Alan`. Agents should respond to mentions addressed to them on their next turn (best-effort, concise).
- Each agent turn should also scan the card comments for unanswered mentions to them and reply (best-effort).

### Pending intake + Kanban move policy

- `Pending` is the first-class pre-PO backlog column. New cards created from `/kanban` start there with `title` + optional short description.
- Runtime/workflow DB is the operational source of truth for these intake cards.
- Desktop drag-and-drop and the mobile move sheet must call the same runtime transition path.
- Successful create/move actions must refresh the Kanban automatically from runtime.
- Raw intake in `Pending` does **not** require immediate OpenSpec artifacts; proposal/spec/tasks/design are created or updated when PO pulls the card into `PO`.
- Kanban moves must respect workflow guard rails: forward progression happens one gate at a time, while sending a card back to an earlier stage is allowed when rework is needed.

### Work-item discipline (inside the existing flow)

- Use `change` as the release container, `story` as the default independently-ownable delivery slice, and `bug` for real defects/blockers.
- Prefer checklist/subtasks for tiny implementation steps; create a separate `story` only when ownership, sequencing, dependency, or visibility really benefits.
- A `story` cannot be considered complete while any child `bug` remains open.
- Default WIP: at most **2 active stories per change** and **1 active story per owner/run** unless there is an explicit reason to exceed it.
- Parallel work is allowed only when lock scope is clear. If two items touch the same delivery surface and safe isolation is uncertain, serialize them.
- Dependencies must be declared before treating a blocked story as active work.

### Tracking consistency (avoid drift)

- Preferred publish sequence for workflow changes: **DEV implements -> QA validates -> commit/publish after QA**.
- Local unpublished changes from the current change should not, by themselves, block `DEV -> QA`.
- If publish/upstream guards are enforced for later gates such as `Alan homologation` or `Archived`, run `./scripts/verify_upstream_published.py --for-status <status>` before that later transition.
- The guard blocks progression when there are relevant tracked/untracked repo changes or unpushed commits; Playwright/QA ephemeral artifacts under `frontend/playwright-report/**`, `frontend/test-results/**`, `qa_artifacts/**`, and similar cache dirs are ignored by default.
- Important: `QA PASS` alone does not justify saying `next step: Alan homologation`. If the publish guard blocks the `QA -> Alan homologation` move, the required handoff is: `QA passed, promotion blocked by upstream publish guard`, plus the unblock owner and explicit confirmation that runtime did **not** advance yet.
- An agent may only claim a work item/stage done after updating:
  1) runtime/Kanban state
  2) Kanban card comment (handoff)
  3) `openspec/changes/<change>/tasks.md` when task checkboxes changed
  4) `docs/coordination/<change>.md` when the audit mirror needs reconciliation
- Stage completion rule: runtime state + handoff comment must both exist in the same turn; otherwise the stage is not operationally complete.
- Guard-rail: if coordination indicates completion but `tasks.md` still has unchecked items, the next turn must be a **tracking reconciliation** (no new implementation) until consistent.
- Guard-rail: if runtime shows a typed blocker/bug/dependency state that is missing from OpenSpec or the coordination mirror, reconcile that tracking drift before claiming fresh progress.
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
