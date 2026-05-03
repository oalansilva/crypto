## Why

Card #102 reports `frontend/tests/kanban-bugs.spec.ts` is outside the executable Playwright suite path, so the bug coverage exists but is not discovered by the standard E2E run.

## What Changes

- Move `kanban-bugs.spec.ts` into the discovered `frontend/tests/e2e/` directory.
- Validate Playwright test discovery includes the Kanban bug tests.
- Keep test behavior unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ci-testing-hardening`: Playwright E2E test discovery includes Kanban bug coverage.

## Impact

- `frontend/tests/e2e/kanban-bugs.spec.ts`
- Playwright E2E discovery/listing
