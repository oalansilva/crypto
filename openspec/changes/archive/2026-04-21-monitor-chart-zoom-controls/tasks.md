## 1. OpenSpec Alignment

- [x] 1.1 Review the scope against `proposal.md`, `design.md`, and the three delta specs before implementation starts
- [x] 1.2 Confirm the change remains limited to the expanded Monitor strategy chart and does not expand to unrelated chart surfaces

## 2. Frontend Implementation

- [x] 2.1 Add explicit zoom-in and zoom-out controls to `frontend/src/components/monitor/ChartModal.tsx`
- [x] 2.2 Implement a helper that reads the current visible logical range and applies proportional zoom steps without refetching candles
- [x] 2.3 Ensure zoom actions preserve selected timeframe, loaded candles, active indicators, and signal markers
- [x] 2.4 Keep the main price panel and RSI panel synchronized after every zoom action
- [x] 2.5 Clamp zoom behavior to avoid collapsing into an unusable candle window

## 3. Validation

- [x] 3.1 Verify manually in `/monitor` that opening a strategy chart exposes working zoom-in and zoom-out controls
- [x] 3.2 Verify zoom does not trigger candle reloads by default and does not break timeframe switching
- [x] 3.3 Verify keyboard focus can reach the zoom controls and activate them
- [x] 3.4 Run relevant frontend tests or targeted validation for the Monitor chart flow
- [x] 3.5 Run `openspec validate monitor-chart-zoom-controls --type change`

> Note: Use project skills (.codex/skills) when applicable for frontend implementation, testing, debugging, and accessibility review.
