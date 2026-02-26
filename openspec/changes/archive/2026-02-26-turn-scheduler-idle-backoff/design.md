## Context

We run a recurring OpenClaw cron job (“Turn Scheduler”) every 15 minutes to pick exactly one PO/DEV/QA item from `docs/coordination/*.md`. When there are no active OpenSpec changes, the job still runs and produces “nothing to do” executions.

Constraints:
- Keep behavior identical when at least one active change exists.
- Avoid additional user notifications during idle.
- Prefer a simple, reversible operational change.

## Goals / Non-Goals

**Goals:**
- Reduce executions when there are no active changes.
- Automatically restore normal cadence when changes reappear.
- Keep notifications policy unchanged (notify only on meaningful state changes).

**Non-Goals:**
- Changing the PO/DEV/QA selection algorithm.
- Adding product features to the crypto app.

## Decisions

1) Implement idle/backoff by controlling cron schedule/enablement
- Option A (preferred): Maintain a lightweight “controller” that periodically checks for active changes and updates the Turn Scheduler job schedule (e.g., 15m when active, 4h when idle).
- Option B: Disable the Turn Scheduler job when idle and re-enable when active.

Rationale: Both approaches are reversible and do not touch app code. Option A avoids fully disabling and keeps periodic self-healing.

2) Keep a minimal notification surface
- Only one notification is permitted when the scheduler switches modes (optional), and otherwise remain silent.

## Risks / Trade-offs

- [Risk] Misconfiguration could leave the scheduler in idle cadence while work exists → Mitigation: keep the controller check reasonably frequent (e.g., hourly) and restore 15m immediately on detection.
- [Risk] Multiple jobs interacting could race → Mitigation: single controller source of truth; idempotent updates.
