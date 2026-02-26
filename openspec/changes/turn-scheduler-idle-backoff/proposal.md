## Why

The Turn Scheduler currently runs every 15 minutes even when there are no active changes, creating unnecessary compute/cost and operational noise.

## What Changes

- Add an **idle backoff** mode for the Turn Scheduler: when there are **no active OpenSpec changes**, it will run less frequently (or pause), and automatically return to the normal cadence when work exists.
- Keep behavior unchanged when there is at least one active change.

## Capabilities

### New Capabilities
- `turn-scheduler-idle-backoff`: Reduce scheduler frequency when there are no active changes, and restore normal frequency when changes exist.

### Modified Capabilities
- (none)

## Impact

- Affects the OpenClaw cron job configuration and/or logic that triggers PO/DEV/QA turns.
- No product API changes.
- Primary benefit is operational (lower cost/less noise) with no change to delivery behavior when work is active.
