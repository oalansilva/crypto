## Context

Favorites analysis navigates to `ComboResultsPage`, which renders the legacy `CandlestickChart`. Monitor renders a richer `ChartModal` based on the same `lightweight-charts` library, using a dark operational canvas, volume, moving averages, trade/signal markers, and explicit zoom controls. The user expectation is that both screens show the same chart style for the same strategy analysis.

## Goals / Non-Goals

**Goals:**
- Align the Favorites analysis chart with the Monitor chart visual language and controls.
- Keep the existing `/combo/results` navigation and saved favorite analysis cache behavior.
- Render BTC/USDT and `multi_ma_crossover` favorite analysis with clear candles, volume, trade markers, and MA overlays.
- Follow `DESIGN.md` dark Binance tokens: `#0b0e11`, `#1e2329`, `#2b3139`, `#eaecef`, `#929aa5`, `#fcd535`, trading green/red.

**Non-Goals:**
- Move Favorites analysis into the Monitor modal.
- Add new backend endpoints or candle-fetch behavior.
- Change strategy calculations or saved metrics.

## Decisions

- Create a reusable Monitor-aligned result chart component for `/combo/results` instead of embedding `ChartModal` directly. `ChartModal` owns modal-only state, timeframe fetching, signal history, and opportunity semantics that do not belong in backtest/favorite results.
- Keep the chart fed by `result.candles`, `result.trades`, and `result.parameters`. This preserves Favorites cache behavior and avoids new API requests when opening saved analysis.
- Add volume and MA overlays derived from visible candles and strategy parameters. This matches Monitor's operational chart vocabulary without depending on backend indicator arrays.
- Keep trade markers from result trades. For Favorites, these are the actionable entry/exit points the user needs to inspect.
- Provide explicit zoom controls and mouse wheel zoom over the chart shell. This matches the Monitor interaction pattern and keeps chart inspection ergonomic.

## Risks / Trade-offs

- Full `ChartModal` feature parity is broader than needed -> implement shared visual/interaction standard first, without timeframe switching.
- Some strategies may not use MA parameters -> default periods keep chart useful while still allowing parameter-derived overlays for `multi_ma_crossover`.
- Result candles may be missing for old favorites -> preserve the empty state and do not block the rest of the result screen.
