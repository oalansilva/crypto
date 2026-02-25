## Context

We want a **mobile-first** monitoring dashboard that feels like a lightweight TradingView, but is limited to the user’s **Favorites** symbols. The dashboard must render **candlestick charts** and allow timeframe switching.

Constraints:
- Reuse existing market data origins where possible:
  - Stocks: Stooq (typically 1d)
  - Crypto: CCXT (supports intraday timeframes like 1h/4h)
- Keep the initial version small and stable; focus on UX and correctness.

## Goals / Non-Goals

**Goals:**
- Add a new dashboard route optimized for mobile.
- Display Favorites symbols and allow selecting a symbol.
- Render candlestick chart for the selected symbol.
- Support timeframe switching (1h/4h/1d) with validation.
- Avoid external UI complexity; keep controls touch-friendly.

**Non-Goals:**
- Full TradingView feature parity (drawing tools, many indicators, multi-pane layouts).
- Storing custom layouts per user.
- Adding new data providers beyond existing Stooq/CCXT.

## Decisions

1) Tabs inside existing Monitor
- Decision: enhance the existing Monitor screen by adding tabs:
  - Status (existing behavior)
  - Dashboard (new mobile-first)
- Rationale: preserves existing workflows while enabling iterative improvements in the same entry point.

2) Candlestick chart library
- Decision: use a lightweight React candlestick chart solution (e.g., `lightweight-charts` wrapper) rather than building custom SVG.
- Rationale: candlestick rendering and time axes are non-trivial; library reduces bugs.

3) Backend candle endpoint
- Decision: add a small backend endpoint that returns OHLC candles for a symbol/timeframe using existing providers.
- Rationale: keeps frontend simple and consistent; provides one contract for both stocks and crypto.

4) Timeframe constraints and provider selection
- Decision: enforce provider-specific timeframe validation:
  - Stocks:
    - `15m`, `1h`, `4h` via Yahoo (intraday with limited history windows)
    - `1d` via Stooq or Yahoo
  - Crypto (ccxt): allow `15m`, `1h`, `4h`, `1d` initially
- Rationale: enables intraday monitoring for stocks while keeping behavior predictable.

5) Favorites as the only dataset
- Decision: dashboard pulls symbols from existing Favorites endpoint/data.
- Rationale: matches user intent and reduces scope.

## Risks / Trade-offs

- [Risk] E2E test flakiness due to charts rendering in headless mode → Mitigation: E2E asserts presence of chart container + basic UI state, not pixel-perfect candles.
- [Risk] Stooq limitations for intraday → Mitigation: show disabled timeframes for stocks and clear validation messages.
- [Risk] Increased frontend bundle size due to chart library → Mitigation: choose small library; lazy-load chart component.

## Migration Plan

1) Add backend candle endpoint and unit/integration tests.
2) Add frontend dashboard route and UI.
3) Add Playwright E2E tests for navigation + timeframe switching.
4) Deploy and verify on mobile.

Rollback: revert the change or hide the dashboard route behind a feature flag.

## Open Questions

- Final route naming: `/dashboard` vs `/monitor2`.
- How many candles to fetch by default (limit) per timeframe.
- Whether to show mini sparklines in the list or only in the selected detail view.
