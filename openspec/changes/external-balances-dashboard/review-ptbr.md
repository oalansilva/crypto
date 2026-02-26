# Revisão (PT-BR) — external-balances-dashboard

## Objetivo
Ter uma tela no app pra ver **saldos/posições via API**. Começando por **Binance Spot** (saldo por ativo, com free/locked/total). IBKR entra depois quando o acesso live estiver liberado.

## O que vai ter
- Endpoint no backend: `GET /api/external/binance/spot/balances`
- Página no frontend: `/external/balances` (ou link no menu) exibindo a lista.

## Segurança
- Credenciais ficam só no **backend (env vars)**.
- Integração **somente leitura**.

## Critérios de aceite
- Mostrar saldos Binance Spot (asset, free, locked, total).
- Destacar quando `locked > 0`.
- Erro claro se chaves não estiverem configuradas.

## Próximo passo
Tu aprovar pra eu implementar.
