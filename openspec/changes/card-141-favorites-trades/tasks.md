## 1. Backend

- [x] 1.1 Extract reusable combo backtest execution helper for favorites trade regeneration.
- [x] 1.2 Add authenticated Favorites trades endpoint with permission checks, saved-trades fast path, regeneration, validation, and lazy persistence.
- [x] 1.3 Add backend tests for saved trades, regeneration, metric validation, and protected access.

## 2. Frontend

- [x] 2.1 Update Favorites `View Trades` to fetch regenerated trades when saved trades are missing.
- [x] 2.2 Add loading/error/mismatch handling without exposing protected favorite details.
- [x] 2.3 Update Favorites E2E coverage for regenerated trades.

## 3. Validation

- [x] 3.1 Run OpenSpec validation for the change.
- [x] 3.2 Run focused backend and frontend validation for the card.

Use project skills when applicable: `$crypto-frontend` for UI changes and `$openspec-apply-change` / `$openspec-verify-change` for implementation and verification.
