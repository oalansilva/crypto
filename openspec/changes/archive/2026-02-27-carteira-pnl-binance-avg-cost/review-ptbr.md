# Revisão (PT-BR) — carteira-pnl-binance-avg-cost

## Objetivo
Na tela **Carteira** (`/external/balances`), mostrar se cada ativo está com **lucro/prejuízo (PnL)**, usando o **preço médio de compra**.

## Escopo (fase 1)
- Binance **Spot**
- Somente pares em **USDT** (ex.: `HBARUSDT`)
- **Preço médio por compras apenas** (ignora vendas nessa fase)

## O que vai aparecer na tela
- Avg Cost (USDT)
- PnL (USD)
- PnL (%)
- Cores: verde lucro / vermelho prejuízo

## Critérios de aceite
- Se existir histórico de compras, mostrar avg cost + PnL.
- Se não existir, mostrar `-`.
- Não executar trades (somente leitura).

## Próximo passo
Tu aprovar (“ok”) pra eu implementar.
