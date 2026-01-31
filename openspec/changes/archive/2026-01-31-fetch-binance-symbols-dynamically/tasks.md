# Tasks: Dynamic Binance Symbols

- [x] Backend: Create `ExchangeService` to encapsulate `ccxt` logic
- [x] Backend: Implement `fetch_binance_symbols` with `load_markets()`
    - [x] Filter logic: Keep only symbols ending in `/USDT`
- [x] Backend: Implement Caching Mechanism
    - [x] Check for `data/symbols_cache.json` validity (< 24h)
    - [x] If valid, load from disk
    - [x] If invalid/missing, fetch from API and save to disk
- [x] API: Create endpoint `GET /api/exchanges/binance/symbols`
- [x] Frontend: Create `useBinanceSymbols` query hook
- [x] Frontend: Replace textual "Symbol" inputs with Autocomplete/Dropdown components in:
    - [x] `ParameterOptimizationPage` (Find New Strategies)
    - [x] `RiskManagementOptimizationPage` (Optimization)
    - [x] `TimeframeOptimizationPage`
- [ ] Verification: Verify dropdown populates with ~1000+ symbols and loads instantly on refresh
