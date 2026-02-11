# Tasks: Upstream Symbol Validation

## 1. Exchange Service Helpers
- [ ] Add `fetch_binance_symbols_async` or lightweight validation method in `app/services/exchange_service.py` (or static method).
- [ ] Ensure symbols cache file (`data/symbols_cache.json`) is populated.

## 2. Implement Validation Logic
- [ ] In `app/routes/lab.py`, inside `_handle_upstream_user_message`:
  - [ ] Add call to fetch valid symbols (using `ExchangeService`).
  - [ ] Normalize Trader-provided symbol (`_normalize_symbol`).
  - [ ] Check if symbol exists in valid list.
  - [ ] Handle invalid case:
    - [ ] Do NOT update `run["input"]["symbol"]`.
    - [ ] Append system error message to `upstream["messages"]`.
  - [ ] Handle valid case:
    - [ ] Proceed as normal.

## 3. Test Cases
- [ ] Valid symbol ("BTC/USDT") -> Accepted, no error.
- [ ] Invalid symbol ("BTC/USTD") -> Rejected, system error in messages.
- [ ] Valid timeframe ("1h") -> Accepted.
- [ ] Invalid timeframe ("37h") -> Rejected (optional scope).
