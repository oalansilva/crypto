## Context

The Playwright suite discovers tests under the configured E2E path. The Kanban bug spec existed one directory above that executable suite, so direct execution by the reported path returned "No tests found".

## Goals / Non-Goals

**Goals:**

- Put the Kanban bug spec in the discovered E2E directory.
- Confirm `npx playwright test --list` sees its test cases.

**Non-Goals:**

- Rewrite the Kanban tests.
- Change Playwright config.
- Change Kanban product behavior.

## Decisions

- Move the file instead of changing global Playwright config. This is the smallest fix and follows existing test organization.

## Risks / Trade-offs

- Any stale command pointing to the old path must be updated to `frontend/tests/e2e/kanban-bugs.spec.ts`.
