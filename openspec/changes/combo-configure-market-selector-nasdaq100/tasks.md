## 1. NASDAQ-100 universe

- [ ] 1.1 Add a versioned NASDAQ-100 ticker list file under `backend/config/` (tickers only)
- [ ] 1.2 Add an API endpoint to return the NASDAQ-100 list to the frontend

## 2. Combo Configure UI

- [ ] 2.1 Add a Market selector (Crypto vs US Stocks) to the `/combo/configure` page
- [ ] 2.2 When market=US Stocks, load NASDAQ-100 tickers and populate the Symbol picker
- [ ] 2.3 When market=US Stocks, enforce timeframe=1d and disable other timeframes
- [ ] 2.4 Ensure run/backtest/optimize requests include `data_source=stooq` for US Stocks and omit it for Crypto

## 3. Tests and docs

- [ ] 3.1 Add a backend test for NASDAQ-100 universe endpoint
- [ ] 3.2 Add a frontend smoke check verifying toggle updates the symbol list and request payload
- [ ] 3.3 Add UI helper text explaining US Stocks uses free EOD (1D) data

## 4. Notes

- [ ] 4.1 Use project skills under `.codex/skills` when applicable (architecture, tests, debugging, frontend)
