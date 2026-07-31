## Context

`ChartModal` já desenha a linha STOP a partir de `opportunity.stop_price`. Credenciais por usuário existem em `user_exchange_credentials`. O cliente Spot só faz GET assinado (account/myTrades). Specs atuais proíbem ordens.

## Goals / Non-Goals

**Goals:**
- Place/cancel stop-limit Spot no preço do STOP do gráfico, 100% free, via botões.
- Status da ordem protetiva ao abrir o gráfico (long + HOLD).
- Mensagens claras para short/EXIT/sem saldo/chave read-only.

**Non-Goals:**
- Futures/short, auto-place, qty parcial, trailing stop, criptografia at-rest.

## Decisions

1. **Tipo de ordem:** `STOP_LOSS_LIMIT` + `SELL` + `GTC`.
2. **limitPrice:** `stopPrice * (1 - 0.001)`, arredondado ao `tickSize`.
3. **quantity:** 100% `free` do asset base, ajustado a `LOT_SIZE` / `minNotional`.
4. **Identidade:** `newClientOrderId` prefixo `cfstop_` para listar/cancelar só ordens do app.
5. **API:**
   - `GET /api/monitor/spot-stop-order?symbol=&opportunity_id=`
   - `POST /api/monitor/spot-stop-order` `{ symbol, opportunity_id, stop_price, direction }`
   - `DELETE /api/monitor/spot-stop-order` `{ symbol, opportunity_id }`
6. **Credencial:** só do usuário logado; sem fallback `.env` de sistema.
7. **UI:** bloco “Proteção Spot” no `ChartModal` quando long + `showEntryStopRows`; confirmação antes do place.
8. **Par:** `symbol` da opportunity (ex. `ETHUSDT`); asset base via exchangeInfo.

## Risks / Trade-offs

- [Chave só read-only] → erro acionável pedindo Spot Trading na Binance.
- [Saldo insuficiente / filtros] → 400 com motivo; não cria ordem parcial silenciosa.
- [Ordem externa no mesmo símbolo] → cancel só cancela `cfstop_*` do app.
- [Short Spot] → botão desabilitado (fora de escopo).

## Migration Plan

1. Ship backend + UI + OpenSpec.
2. Usuário atualiza chave com Spot trading se quiser usar.
3. Rollback: remover rotas/UI; ordens abertas na Binance permanecem até cancel manual.

## Open Questions

- Nenhum bloqueante para o MVP.
