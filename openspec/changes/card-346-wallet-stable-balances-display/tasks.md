## 1. OpenSpec e preflight

- [x] 1.1 Publicar artifacts OpenSpec no issue #346 (Gist + comentário)
- [x] 1.2 Confirmar `Status=Pronto para Dev` (aprovação humana) antes de codar; branch `change-346-wallet-stable-balances-display`

## 2. Backend — valoração e listagem de stables

- [x] 2.1 Garantir fallback `price_usdt=1.0` para stables de display (USDT/USDC e alinhados a `STABLE_ASSETS`) quando não houver ticker
- [x] 2.2 Não omitir row de stable com `total > 0` por `value_usd=null`; incluir no `total_usd`
- [x] 2.3 Definir `avg_cost_usdt=1.0` para stables na montagem do snapshot (PnL ≈ 0) sem depender do top-N de trades
- [x] 2.4 Tratar wrappers Earn `LDUSDT`/`LDUSDC` (e `LD*`+stable) como stable de display (~1 USD) para não sumirem da Carteira
- [x] 2.4 Testes unit/integration: snapshot com USDT+USDC presentes, dust default e `min_usd=0`
- [x] 2.5 Preferir Simple Earn API (`/sapi/v1/simple-earn/flexible/position` + locked) sobre LD* incompleto; fallback LD* se Earn indisponível

## 3. Frontend — Carteira

- [x] 3.1 Propagar `min_usd` no `authFetch` de `/external/binance/spot/balances`
- [x] 3.2 Confirmar que USDT/USDC renderizam na lista e entram no total visível; copy curta no dust se útil
- [x] 3.3 E2E/visual proporcional da Carteira com stables visíveis (atualizar baseline se UI mudar de propósito)

## 4. Fechamento técnico

- [ ] 4.1 Code Review no diff + commit/push + PR develop
- [ ] 4.2 QA gate verde + merge + `./restart` + Done técnico no #346
