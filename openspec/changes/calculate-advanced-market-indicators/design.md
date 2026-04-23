## Context

The existing `market-indicators` capability persists EMA/SMA/RSI/MACD in `market_indicator` and validates them against TradingView fixtures. Advanced indicators already exist partially in strategy engines, but those values are calculated inline for strategy execution and are not available as persisted, audit-ready scoring features.

This change extends the dedicated market indicator pipeline to cover Bollinger Bands, ATR, Stochastic, OBV, and Ichimoku across active timeframes. The implementation must preserve the current incremental recompute behavior, PostgreSQL runtime requirement, and `market_indicator` uniqueness model.

## Goals / Non-Goals

**Goals:**

- Add persisted advanced indicator vectors for every processed `symbol`/`timeframe` candle.
- Keep runtime calculation deterministic and aligned with documented formulas.
- Preserve incremental/idempotent recompute semantics.
- Document formulas, default parameters, displacement rules, and validation tolerances.
- Validate advanced indicators against three reference sources where practical:
  - TradingView exported fixtures.
  - TA-Lib output for indicators supported by TA-Lib.
  - Independent formula implementation documented in tests/specs.

**Non-Goals:**

- Redesign the strategy engine or combo strategy authoring model.
- Add UI controls for advanced indicators.
- Add new trading signals or change scoring weights.
- Support arbitrary user-defined indicator formulas.
- Replace the existing basic indicator fields.

## Decisions

### Decision: Extend the dedicated market indicator pipeline

Advanced indicators should be calculated in `MarketIndicatorService` rather than only in strategy classes. This keeps scoring consumers on the same persistent source as basic indicators and avoids recalculating features inline.

Alternative considered: reuse `DynamicStrategy` calculations directly. Rejected because strategy calculations are parameterized for strategy execution, have different column naming, and are not persisted with recompute metadata.

### Decision: Prefer explicit columns unless schema pressure requires JSONB

The default implementation path is to add explicit numeric columns for stable default indicators:

- `bb_upper_20_2`, `bb_middle_20_2`, `bb_lower_20_2`
- `atr_14`
- `stoch_k_14_3_3`, `stoch_d_14_3_3`
- `obv`
- `ichimoku_tenkan_9`, `ichimoku_kijun_26`, `ichimoku_senkou_a_9_26_52`, `ichimoku_senkou_b_9_26_52`, `ichimoku_chikou_26`

Alternative considered: store all advanced values in a generic JSONB payload. Rejected as the default because scoring queries and parity tests benefit from typed, directly selectable columns. JSONB remains acceptable only if implementation proves the explicit column set causes migration or compatibility issues.

### Decision: Use TA-Lib where it matches the documented formula

Use TA-Lib for:

- Bollinger Bands: `BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)`.
- ATR: `ATR(high, low, close, timeperiod=14)`.
- Stochastic: `STOCH(high, low, close, fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)`.
- OBV: `OBV(close, volume)`.

Ichimoku is implemented directly because TA-Lib does not provide an Ichimoku function in the Python supported function list.

Alternative considered: implement every formula manually. Rejected because TA-Lib is already the runtime engine for basic indicators and reduces divergence for supported indicators.

### Decision: Implement Ichimoku from documented high/low midpoints

Ichimoku must use highest-high and lowest-low windows:

- Tenkan: `(highest_high(9) + lowest_low(9)) / 2`
- Kijun: `(highest_high(26) + lowest_low(26)) / 2`
- Senkou A: `(Tenkan + Kijun) / 2`, plotted 26 periods forward
- Senkou B: `(highest_high(52) + lowest_low(52)) / 2`, plotted 26 periods forward
- Chikou: close plotted 26 periods backward

The persisted row must document whether displaced spans are stored at their plotted timestamp or as raw values on the source candle timestamp. The preferred model is to store the values aligned to the source candle timestamp and document displacement metadata, because the table key represents candle close time.

Alternative considered: physically shift Senkou/Chikou values into future/past table rows. Rejected because it can create values for timestamps without source candles and complicates idempotent upserts.

### Decision: Cross-validation is evidence, not runtime dependency

Runtime calculation should not call TradingView or external documentation sources. Cross-validation belongs in tests and QA artifacts:

- TradingView fixture parity validates platform-visible values.
- TA-Lib parity validates supported runtime engine outputs.
- Independent formula parity validates formulas and catches implementation mistakes.

Ichimoku uses TradingView fixture parity plus independent formula parity; TA-Lib is not applicable for that indicator.

## Risks / Trade-offs

- [Risk] TradingView defaults can differ from TA-Lib defaults, especially ATR smoothing and Stochastic variants. -> Mitigation: document exact parameters, export fixtures with matching defaults, and set indicator-specific tolerances.
- [Risk] Ichimoku displacement semantics can be ambiguous in a row-oriented store. -> Mitigation: store source-aligned values and include displacement metadata in formula docs and tests.
- [Risk] Adding many columns can make future indicator expansion cumbersome. -> Mitigation: keep this change scoped to named default indicators and revisit JSONB only when indicator count becomes dynamic.
- [Risk] Existing strategy implementations may contain formula drift. -> Mitigation: do not treat strategy code as the source of truth; align shared helpers or tests to the documented formulas before reuse.
- [Risk] Backfilling all active symbols/timeframes can be expensive. -> Mitigation: reuse incremental recompute windows and provide force-full recompute only for explicit operational backfill.

## Migration Plan

1. Add the advanced indicator storage fields through a PostgreSQL migration and startup schema guard.
2. Extend `MarketIndicatorService._compute_indicators` to calculate the default advanced indicators.
3. Extend read/upsert paths so latest and time-series APIs include advanced fields.
4. Add formula documentation and fixture metadata.
5. Add parity tests with TradingView fixtures, TA-Lib outputs, and independent formula calculations.
6. Run a controlled recompute/backfill for target symbols/timeframes.

Rollback strategy: keep new columns nullable, deploy code so old rows remain readable, and disable advanced consumers if parity tests fail. A rollback can leave nullable columns in place without breaking existing basic indicator reads.

## Open Questions

- Which symbols/timeframes are the minimum required TradingView fixture set for final QA: current BTCUSDT/NVDA `1d` and `1h`, or an added intraday crypto timeframe?
- Should scoring consume every advanced field immediately, or should this change only make the fields available for future scoring rules?
- Should advanced indicator columns be included in all existing indicator API responses by default, or gated behind a version/field selection parameter?
