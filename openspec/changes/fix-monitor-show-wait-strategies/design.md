## Context

`/api/opportunities/?tier=1` already returns both starred BTC/USDT strategies for Alan:

- `122` `multi_ma_crossoverV2`, status `BUY_NEAR`, `is_holding=false`
- `200` `quant_btc_1d_roc_ema_momentum_guard_long_v3`, status `EXITED`, `is_holding=false`

The UI hid `122` because the backend emitted `BUY_NEAR`, `resolveOpportunitySignal()` mapped it to `wait`, and `MonitorStatusTab` renders only `hold` and `exit`.

## Decision

Make Monitor classification binary end to end:

- `hold`: confirmed active buy/position states.
- `exit`: every non-hold, sell, exited, neutral, unknown, or near-entry state.

The backend opportunity response exposes only `HOLD` or `EXIT` in `status`. The frontend still tolerates legacy raw values defensively, but it resolves them to Compra/Venda immediately. No visible `wait` section, no `Espera` label, and no hidden bucket for starred strategies.

## Scope

- Update frontend signal resolver types and visual mapping.
- Simplify Monitor section types to `hold | exit`.
- Normalize backend opportunity payload status to `HOLD` or `EXIT`, including cached responses.
- Update Monitor Telegram alerts to observe/send only `HOLD` and `EXIT`.
- Update tests so a `BUY_NEAR` starred strategy renders as Venda/Exit, not hidden.

## Risks

- Existing tests may encode old "hide Espera" behavior. Update only tests that describe Monitor public behavior; do not change backend alert internals that still use raw status names.
