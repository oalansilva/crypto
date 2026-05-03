## Why

When an opportunity is already in `exit`, old `entry` and `stop` prices from the previous operation are no longer actionable. Keeping them in the monitor detail views creates noise and can suggest an active setup when the position is already closed.

## What Changes

- Hide `entry` and `stop` rows in `OpportunityCard` when the resolved section is `EXIT`.
- Hide `entry` and `stop` rows in `ChartModal` risk block when the resolved section is `EXIT`.
- Keep current price, distance-to-stop and distance-to-next-status context visible so users can still evaluate the post-exit state.

## Impact

- Frontend: monitor detail panel (`OpportunityCard`) and chart modal (`ChartModal`) conditional rendering behavior.
