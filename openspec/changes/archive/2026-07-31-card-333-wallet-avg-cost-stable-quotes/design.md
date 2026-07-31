## Context

Carteira usa `compute_avg_buy_cost_usdt(asset)` → só `ASSETUSDT` → última compra. Compra ETH em USDC (ordem 10704222824 @ 1920,42) não entra; UI mostra avg ~2247 de outro trade USDT. Vale para qualquer asset do snapshot.

## Goals / Non-Goals

**Goals:**
- Para cada asset não-estável do snapshot, buscar última compra em `ASSETUSDT` e `ASSETUSDC`.
- Usar a compra mais recente entre esses pares como `avg_cost_usdt` (campo mantido; valor em USD estável).
- Regressão: só-USDT continua ok; sem trades → null.
- Testes unitários da seleção multi-quote.

**Non-Goals:**
- Média ponderada de todo o histórico (Alan já pediu última compra).
- Futures/margin.
- Mudança de UI além do número correto.

## Decisions

1. **Quotes:** `USDT` + `USDC` (estáveis 1:1 para PnL da carteira).
2. **Regra:** última compra (`isBuyer`) por `time` entre todos os trades dos pares tentados.
3. **API shape:** manter `avg_cost_usdt` (compat); semanticamente “custo ref. em USD estável”.
4. **Fetch:** uma chamada `myTrades` por par; falha/vazio em um par não bloqueia o outro.
5. **Stables (USDT/USDC/...):** continuam custo `1.0`.

## Risks / Trade-offs

- [Mais latência por asset (2 calls)] → já há `max_trade_symbols` + budget de tempo no snapshot.
- [USDC≠USDT em stress] → aceitável para carteira Spot retail; documentar.

## Migration Plan

1. Ship backend + testes.
2. Sem migração de dados.
3. Rollback: reverter função.

## Open Questions

- Nenhum bloqueante.
