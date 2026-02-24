## Why

The Combo Configure flow is currently optimized for crypto pairs (e.g., `BTC/USDT`). We want users to run the same combo strategies on US stocks using a free EOD (1D) data source, by selecting the market directly on the Combo Configure page.

## What Changes

- Add a Market selector on `/combo/configure` allowing **Crypto** (default) and **US Stocks (NASDAQ-100)**.
- When **US Stocks** is selected:
  - the Symbol control becomes a NASDAQ-100 ticker picker
  - requests are sent with `data_source=stooq`
  - timeframe is enforced to `1d` (EOD)
- When **Crypto** is selected, behavior remains unchanged.

## Capabilities

### New Capabilities
- `us-stocks-universe-nasdaq100`: Provide a versioned NASDAQ-100 ticker universe and expose it to the frontend.

### Modified Capabilities
- `frontend-ux`: Combo Configure must support market selection and pass `data_source` based on the chosen market.

## Impact

- Frontend: Combo Configure page UI (new selector + symbol picker behavior + timeframe enforcement).
- Backend: a simple endpoint to return NASDAQ-100 tickers.
- Existing crypto flows remain unchanged.
