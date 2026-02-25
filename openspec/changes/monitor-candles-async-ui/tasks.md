## 1. Frontend: Async Candles Fetch Behavior

- [ ] 1.1 Add an in-memory candles cache keyed by `symbol|timeframe`
- [ ] 1.2 Add per-symbol request cancellation (AbortController) so last-click wins
- [ ] 1.3 Treat AbortError as non-error and do not show it to the user

## 2. Frontend: UI Responsiveness

- [ ] 2.1 Make timeframe selection optimistic (update selected state immediately)
- [ ] 2.2 Show a small loading indicator confined to the chart area
- [ ] 2.3 Ensure other card interactions remain usable while candles load (Portfolio, Price/Strategy)
- [ ] 2.4 Ensure scrolling the list remains possible while candles load

## 3. Tests (Playwright)

- [ ] 3.1 Add/update E2E test: switching timeframe does not block other interactions
- [ ] 3.2 Add/update E2E test: loading indicator appears only in chart area

## 4. Validation

- [ ] 4.1 Run `openspec validate monitor-candles-async-ui --type change`

> Note: Use project skills (.codex/skills) when applicable (architecture, tests, debugging, frontend).
