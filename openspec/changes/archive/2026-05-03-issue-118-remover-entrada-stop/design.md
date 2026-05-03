## Context

`resolvedSignal.section` already classifies opportunities as `hold`, `wait`, or `exit` in `resolveOpportunitySignal`.

`OpportunityCard` and `ChartModal` currently always render operational `entry` and `stop` values, independent of status.

## Decisions

1. Use a single status check in the UI layer:
   - `const showEntryStopRows = resolvedSignal.section !== 'exit'`.

2. Keep the rest of risk/detail information in place for `EXIT` rows.

3. When `showEntryStopRows` is false:
   - hide the two lines (`entry`, `stop`) in `OpportunityCard`'s operational block.
   - hide the two lines (`Entry`, `Stop`) in `ChartModal` "Risk / Stop" block.
   - keep `current price` and `risk` metrics visible.

## Validation

- Visual/manual check in `develop` for an `exit`-classified row.
- Keep OpenSpec validation/traces in line with project flow at lote/release.
