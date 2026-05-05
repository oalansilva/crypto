## Context

The current signal visual model uses one label for both chart marker and distance target. For `HOLD`, that label is `EXIT` because the next decision is exit. On the chart, though, a down arrow labeled `EXIT` reads as an executed sell, not an active long position.

## Decision

Extend the Monitor signal visual data with a separate `distanceLabel`. Keep `markerLabel` as current visual state and use:
- `HOLD`: marker `LONG`, green up arrow below the bar; distance label `exit`.
- `EXIT`: marker `ENTRY`, blue down arrow as existing re-entry/exit context; distance label `entry`.
- `WAIT`: marker `WAIT`; distance label from current wait state.

## UI/UX

No layout change. This keeps the operational chart compact while making the visible marker consistent with the list state. The chart still shows distance to the next decision, so the trader can see exit proximity without mistaking it for a sold position.

## Testing

Add a focused Playwright test that opens a HOLD opportunity with no historical signal markers and asserts:
- chart badge remains `HOLD`;
- signal context shows active position text;
- distance label says `To exit`;
- the current marker label does not appear as `EXIT`.
