# Change Proposal: Upstream Symbol Validation

## Problem
The Trader (LLM) currently accepts any symbol provided by the user (or hallucinated) without validation against the exchange (Binance).
If an invalid symbol (e.g., "BTC/USTD" with a typo) is passed to the execution phase, it causes fatal errors in the data loader, potentially crashing the backend or causing infinite retry loops.

## Solution
Implement a validation step in the upstream chat handler (`_handle_upstream_user_message`):
1. When the Trader extracts a `symbol`, check if it exists in the Binance exchange (using cached symbols from `ExchangeService`).
2. If invalid:
   - **Reject the symbol update** (do not save it to `run["input"]`).
   - Inject a system error message into the upstream chat history: "System: Symbol '{symbol}' not found in Binance USDT pairs. Please ask the user to correct it."
   - The Trader will see this error in the next turn and ask the user for clarification.
3. If valid:
   - Proceed as normal.

## Scope
- Backend: `app/routes/lab.py` (upstream handler).
- Service: `app/services/exchange_service.py` (ensure caching works correctly).

## Impact
- Prevents invalid symbols from reaching execution phase.
- Improves user experience by catching typos immediately in the chat.
- Reduces backend stability risks.
