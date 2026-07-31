## Why

Na Carteira, saldos Spot em stablecoins (USDT, USDC e demais stables suportadas) deixam de aparecer ou não entram no total, mesmo com saldo na Binance. O usuário não vê a liquidez em caixa e o total da carteira fica incompleto. O bug foi reportado em PROD/DEV após o card `#333` (avg cost com quotes USDC), que tocou o mesmo domínio sem garantir a listagem das próprias stables.

## What Changes

- Garantir que saldos Spot de stables (pelo menos USDT e USDC) com `total > 0` apareçam na Carteira com `price_usdt ≈ 1` e `value_usd` coerente.
- Incluir esses saldos no `total_usd` da resposta e da UI.
- Propagar o controle de dust da Carteira (`min_usd`) até a API, alinhado ao spec existente.
- Evitar que a regra `STABLE_ASSETS` (custo 1.0) seja confundida com exclusão da lista.
- Cobrir com testes backend (+ E2E/visual proporcionais da Carteira com USDT/USDC).

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `external-balances`: exigir listagem e valoração de saldos Spot de stables na Carteira; dust configurável sem sumir stables materiais; wiring `min_usd` da UI.

## Impact

- Backend: `binance_spot.py`, `binance_prices.py`, rota `/external/binance/spot/balances`.
- Frontend: `ExternalBalancesPage.tsx` (query `min_usd`, exibição de linhas stable).
- Specs: `openspec/specs/external-balances`.
- UI impact: **affected** (Carteira — linhas/total). Gate de Design obrigatório antes do DEV.
- Relacionado: `#333` (não reabrir escopo de PnL de assets não-stable).
