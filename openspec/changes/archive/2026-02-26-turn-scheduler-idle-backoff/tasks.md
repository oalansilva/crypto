## 1. Discovery

- [ ] 1.1 Identify the current Turn Scheduler cron job id and current schedule settings
- [ ] 1.2 Confirm the desired idle behavior (backoff interval vs disable) and the target idle interval (e.g., 1h/4h)

## 2. Implementation

- [ ] 2.1 Implement an idle/backoff controller (job or logic) that detects “no active changes”
- [ ] 2.2 Update the Turn Scheduler schedule to normal (15m) when active changes exist
- [ ] 2.3 Update the Turn Scheduler schedule to idle cadence (reduced frequency) when no active changes exist
- [ ] 2.4 Ensure updates are idempotent and do not spam notifications

## 3. Validation

- [ ] 3.1 Test: with no active changes, verify the Turn Scheduler no longer runs every 15 minutes
- [ ] 3.2 Test: create an active change and verify the Turn Scheduler returns to 15-minute cadence
- [ ] 3.3 Document the new behavior in coordination README or relevant docs

## 4. Ops / Rollback

- [ ] 4.1 Define rollback steps (restore fixed 15-minute schedule)
- [ ] 4.2 Apply branch protection / required checks policy only if needed (no change by default)

> Note: use existing project skills/tools (.codex/skills) for debugging and validation where applicable.
