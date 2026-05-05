## Context

The current signal visual model uses one label for both chart marker and distance target. For `HOLD`, that label is `EXIT` because the next decision is exit. On the chart, though, a down arrow labeled `EXIT` reads as an executed sell, not an active long position.

## Decision

Extend the Monitor signal visual data with a separate `distanceLabel`. Keep `markerLabel` as current visual state and use:
- `HOLD`: marker `LONG`, green up arrow below the bar; distance label `exit`.
- `EXIT`: marker `ENTRY`, blue down arrow as existing re-entry/exit context; distance label `entry`.
- `WAIT`: marker `WAIT`; distance label from current wait state.

For position state, use the generated signal frame as the source of truth for latest entry/exit order. `ComboStrategy.generate_signals` delays confirmed rules to the next candle open, so a current execution signal can exist one candle after the indicator reference candle. Backend `is_holding`, list grouping, and chart resolution must all use that same generated signal order.

`EXIT_SIGNAL` is an exit decision. If a latest visible exit signal matches the chart candle, the chart can resolve `EXIT` even when the distance reference candle is the prior closed candle.

## UI/UX

No layout change. This keeps the operational chart compact while making the visible marker consistent with the list state. The chart still shows distance to the next decision, so the trader can see exit proximity without mistaking it for a sold position.

## Testing

Add a focused Playwright test that opens a HOLD opportunity with no historical signal markers and asserts:
- chart badge remains `HOLD`;
- signal context shows active position text;
- distance label says `To exit`;
- the current marker label does not appear as `EXIT`.

Add regression coverage for a current exit signal after an active entry:
- backend unit coverage verifies last buy/sell positions come from the generated signal frame;
- Playwright coverage verifies the list row and chart badge both resolve `EXIT`.
