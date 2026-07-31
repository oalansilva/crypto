## Why

A Carteira calcula preço médio/PnL só com trades `ASSETUSDT`. Compras reais em USDC (ex.: ETH) geram avg cost e PnL errados. O bug vale para todos os ativos do snapshot, não um símbolo isolado.

## What Changes

- Ampliar a regra de custo de referência para considerar quotes estáveis relevantes (**USDT e USDC**) para **cada** asset da Carteira.
- Escolher a compra mais recente entre os pares suportados (mantém a regra operacional atual de “última compra”).
- Atualizar spec `external-balances` (sair do “phase 1 = só USDT”).
- Cobrir com testes multi-asset / USDC + regressão USDT.

## Capabilities

### New Capabilities
- _(nenhuma)_

### Modified Capabilities
- `external-balances`: avg cost/PnL usam trades Spot em USDT e USDC para todos os ativos do snapshot.

## Impact

- Backend: `binance_trades.py` (+ callers/testes).
- Frontend: sem mudança de contrato esperada (`avg_cost_usdt` permanece; valor passa a refletir última compra estável correta).
- OpenSpec delta em `external-balances`.
