## Why

Cards #202, #203, and #204 address the same trader-facing gap: strategy identity must be clear and optimization results must be produced by the same execution mode used for scoring. Today the product can show only a name, hide the raw Strategy field in Favorites, and return final optimization trades from fast execution even when Deep Backtest was requested.

## What Changes

- Add public, high-level strategy descriptions for combo templates.
- Surface strategy descriptions consistently in Combo, Favorites, and Monitor.
- Show the Strategy field explicitly in the Favorites grid/card while preserving protected-user redaction.
- Ensure `/api/combos/optimize` final returned trades/metrics use Deep Backtest when optimization used Deep Backtest.
- Add focused backend/frontend tests for the new contracts.

## Capabilities

### New Capabilities

- `strategy-template-descriptions`: Public, trader-friendly descriptions for strategy templates across Combo, Favorites, and Monitor.

### Modified Capabilities

- `favorites`: Favorites SHALL expose the Strategy field and high-level strategy description in the visible grid/card.
- `monitor`: Monitor SHALL expose the high-level strategy description in rows/details where strategy identity is shown.
- `combo-optimizer`: Optimization final trades and metrics SHALL use the same deep/fast execution mode requested for scoring.

## Impact

- Backend: combo metadata, favorite responses, opportunity responses, optimizer final backtest path.
- Frontend: Combo template list, Favorites grid/mobile cards, Monitor rows/details.
- Tests: focused unit/integration tests and frontend build/type validation.
