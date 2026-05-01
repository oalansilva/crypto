## Why

Issue #82 reports that the Monitor chart modal can hide the resolved signal context expected by QA. Without this block, the trader loses the explanation for why a raw EXIT signal is being treated as WAIT.

## What Changes

- Ensure the Monitor chart modal exposes the resolved signal state and timeframe/candle context in the non-algorithmic chart view.
- Keep the visible badge, card state, and modal context aligned for mismatched exit signals.
- Preserve existing compact/non-compact modal behavior and chart interactions.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `opportunity-monitor`: The Monitor chart modal must show explicit resolved-state context for strategy signal decisions.

## Impact

- Frontend Monitor chart modal rendering.
- Signal resolution context displayed to the trader.
- Playwright E2E coverage for mismatched exit signals in the Monitor modal.
