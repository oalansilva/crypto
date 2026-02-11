# Design: Upstream Symbol Validation

## Overview
Validate symbols in the upstream chat loop (`app/routes/lab.py`) before accepting inputs.

## Components
- **ExchangeService**: Provides `fetch_binance_symbols()` (cached).
- **Lab Routes**: `_handle_upstream_user_message` function in `lab.py`.
- **System Injection**: Inject system-role messages into upstream history.

## Flow
1. User sends message (e.g., "Use BTC/USTD").
2. Trader (LLM) extracts inputs: `inputs: { "symbol": "BTC/USTD" }`.
3. `_handle_upstream_user_message`:
   - Extracts symbol: "BTC/USTD".
   - Calls `ExchangeService.validate_symbol("BTC/USTD")`.
   - If invalid:
     - Log error.
     - Append `{"role": "system", "text": "Error: Symbol 'BTC/USTD' not found..."}` to upstream messages.
     - **DO NOT** update `run["input"]["symbol"]`.
     - Continue to next turn (Trader sees error).
   - If valid:
     - Update `run["input"]["symbol"]`.
     - Continue normal flow.

## Edge Cases
- **Cache Miss**: If cache is empty, fetch from API (blocking once).
- **Network Error**: If API fails, allow symbol (fail open) to avoid blocking valid inputs.
- **Case Sensitivity**: Ensure symbol comparison is case-insensitive or normalized (upper case).
