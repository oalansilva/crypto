## Why

The Monitor currently receives starred BTC strategies from the backend but can hide a strategy when the resolver classifies it as `WAIT`/`BUY_NEAR`. Alan confirmed the Monitor concept must be binary: Compra/Hold or Venda/Exit.

## What Changes

- Remove `WAIT`/`Espera` as a Monitor decision concept in backend API and frontend UI.
- Normalize backend opportunity `status` to only `HOLD` or `EXIT`.
- Resolve starred non-hold strategies into the Venda/Exit section instead of hiding them.
- Keep Compra/Hold for active buy/position states.
- Add regression coverage for two starred BTC/USDT strategies appearing in Monitor even when one is `BUY_NEAR`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `monitor`: Monitor decision display becomes binary: Compra/Hold or Venda/Exit.
- `opportunity-monitor`: Non-hold starred opportunities remain visible as Venda/Exit instead of becoming hidden wait rows.

## Impact

- Frontend Monitor signal resolver and section grouping.
- E2E Monitor regression tests.
- Backend opportunity API status contract.
- Monitor Telegram alert status handling.
