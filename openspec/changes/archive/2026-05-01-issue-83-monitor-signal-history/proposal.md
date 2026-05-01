## Why

Issue #83 reports that the Monitor chart modal does not expose recent `Signal History` entries from the strategy payload. The current Monitor layout uses a visible table row while the older QA path targets a hidden expanded detail card, so the modal is never opened through the active workflow.

## What Changes

- Align the E2E path with the current visible Monitor row workflow.
- Verify the chart modal shows `Signal History` with recent `ENTRY` and `EXIT` entries from `signal_history`.
- Preserve existing chart modal rendering and marker alignment behavior.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `opportunity-monitor`: The Monitor chart modal must expose recent entry/exit history when strategy payload includes `signal_history`.

## Impact

- Frontend Monitor E2E coverage.
- Opportunity Monitor spec for signal-history context.
