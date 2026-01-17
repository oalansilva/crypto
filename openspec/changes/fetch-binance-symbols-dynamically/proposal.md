# Dynamic Binance Symbols Fetching

## Problem
Currently, the system relies on users manually typing raw symbol strings (e.g., "BTC/USDT") or uses hardcoded defaults in tests/presets. This leads to:
1.  **User Error**: Typos in symbol names cause backtest failures.
2.  **Stale Data**: Users might not know which new pairs are available on Binance.
3.  **Poor UX**: No autocomplete or validation for available markets.

## Solution
Integrate with the Binance API (via `ccxt`) to fetch the list of available trading pairs dynamically.
To optimize performance and avoid hitting rate limits or slowing down the UI:
1.  **Fetch**: Use `ccxt.binance().load_markets()` to get all active symbols.
2.  **Filter**: Process the list to keep **only** symbols ending in `/USDT` (e.g., `BTC/USDT`, `ETH/USDT`), discarding others like `/BTC`, `/ETH`, or `/BUSD`.
2.  **Cache**: Store the result locally to serve subsequent requests instantly.
    *   **Level 1 (MVP)**: JSON file cache (`symbols_cache.json`) valid for 24 hours.
    *   **Level 2 (Scale)**: In the future, if the dataset grows or we need distributed processing, this can be moved to Spark or Redis, but file caching is sufficient for the current scale (~1500 pairs).
3.  **API**: Expose `GET /api/symbols` to the frontend.
4.  **Frontend**: Populate the symbol selector with this dynamic list.

## Risks
-   **Rate Limits**: Binance API has strict rate limits; caching is critical.
-   **Startup Time**: First fetch might take a few seconds; needs loading state in UI.
-   **Data Consistency**: Backtesting requires historical data; fetching a symbol here doesn't guarantee we have history for it context-aware checks might be needed.
