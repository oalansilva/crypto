## 1. Shared Chart Surface

- [x] 1.1 Extract a reusable `StrategyChartSurface` from the Favorites chart behavior.
- [x] 1.2 Support candles, volume, markers, visible bar count, explicit zoom, wheel zoom and optional price lines.
- [x] 1.3 Apply `DESIGN.md` tokens and keep prototype-inspired chart-first structure.

## 2. Favorites Integration

- [x] 2.1 Convert `MonitorAlignedCandlestickChart` into a wrapper over the shared surface.
- [x] 2.2 Preserve Favorites result payload behavior and existing Playwright selectors.

## 3. Monitor Integration

- [x] 3.1 Refactor `ChartModal` to use the shared surface and remove duplicated chart setup.
- [x] 3.2 Preserve timeframe switching, signal context, signal history markers, fallback marker and entry/stop price lines.
- [x] 3.3 Preserve existing Monitor Playwright selectors.

## 4. Validation

- [x] 4.1 Run `openspec validate --all`.
- [x] 4.2 Run frontend build.
- [x] 4.3 Run focused Favorites and Monitor E2E specs.
