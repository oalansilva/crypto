## Context

The Monitor now uses table rows with expandable detail cards. Some E2E tests still assumed cards were always present and visible. Hidden DOM rows made selectors misleading because tests could find stale or collapsed card content instead of validating the active user flow.

## Goals / Non-Goals

**Goals:**

- Make collapsed rows truly absent from the detail-card DOM.
- Require tests to expand rows before asserting card-only controls.
- Preserve table-first scanning behavior.

**Non-Goals:**

- Redesign Monitor UI.
- Change portfolio, mode, timeframe, or strategy preference behavior.

## Decisions

- Conditionally render `<tr className="detail-row">` only when the row is expanded.
- Keep `monitor-row-*` as the stable selector for collapsed table rows.
- Keep `monitor-card-*` as the stable selector for expanded detail cards.

## Risks / Trade-offs

- Tests must explicitly expand rows before card assertions. This is more verbose, but it matches the actual UI contract.
