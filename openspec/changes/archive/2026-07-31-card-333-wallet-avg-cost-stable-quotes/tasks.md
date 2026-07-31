## 1. OpenSpec e card

- [x] 1.1 Publicar artifacts OpenSpec no issue #333
- [x] 1.2 Confirmar Status=In Progress e branch `change-333-wallet-avg-cost-usdc-quotes`

## 2. Backend

- [x] 2.1 Ampliar `compute_avg_buy_cost_usdt` para buscar última compra em USDT + USDC por asset
- [x] 2.2 Helper de seleção da compra mais recente entre múltiplos pares
- [x] 2.3 Manter custo `1.0` para stables e `null` sem trades

## 3. Testes

- [x] 3.1 Unit: USDC mais recente ganha de USDT antigo (caso ETH-like)
- [x] 3.2 Unit/regressão: só USDT; sem trades; multi-asset sem hardcode
- [x] 3.3 Ajustar integração de balances/PnL se mock de `fetch_my_trades` exigir

## 4. Fechamento

- [x] 4.1 Code Review + commit/push + PR develop
- [x] 4.2 QA gate verde + merge + `./restart` + Done técnico
