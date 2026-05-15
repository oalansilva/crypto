## Why

Alan asked that charts stop showing technical indicators and focus on Buy/Sell signals. The current Monitor chart still exposes moving-average overlays, indicator toggles, and indicator legends, which adds noise to the beta user flow.

## What Changes

- Remove visible technical indicator overlays from Monitor chart rendering.
- Remove chart indicator toggle controls and footer legend entries.
- Keep candlesticks, zoom controls, timeframe controls, and Compra/Venda signal markers.
- Preserve non-chart contextual panels such as candle, risk, and signal history.

## Capabilities

### New Capabilities

### Modified Capabilities
- `monitor`: Monitor chart modal must render a clean signal-focused chart without visible technical indicators.

## Impact

- Frontend Monitor chart modal UI and chart series setup.
- OpenSpec delta for Monitor behavior.
- Focused frontend tests/build validation.
