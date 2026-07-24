## Context

Três superfícies admin legado ainda existem no app:

| Superfície | Frontend | Backend exclusivo |
|---|---|---|
| Backtests (Signals) | `/signals` + `SignalsPage` + `components/signals/*` | `/api/signals` |
| Histórico de Sinais | `/signals/history` + `SignalsHistoryPage` | `/api/signals/history`, `/api/signals/stats` |
| Distribuição de supply | `/supply-distribution` + `SupplyDistributionPage` | `/api/onchain/glassnode/{asset}/supply-distribution` |

Homônimos ativos (não remover): `signal_history` do Monitor/Favoritos/Combo Results; `glassnode_service` compartilhado; mining-metrics e exchange-flows.

## Goals / Non-Goals

**Goals:**

- Remover UI, nav, rotas e APIs exclusivas das três superfícies.
- Manter Monitor, Favoritos, Combos e demais frentes operacionais.
- Atualizar testes e delta OpenSpec para refletir a remoção.

**Non-Goals:**

- Não dropar tabela `SignalHistory` nem migrations históricas.
- Não remover `ai_dashboard`, `signal_monitor` ou `signal_feed_snapshot_worker` nesta change (dependências cruzadas; card futuro se Alan pedir purge total).
- Não remover Glassnode connector nem demais métricas onchain.

## Decisions

1. **Corte na borda do produto descontinuado** — apagar páginas/rotas/nav e routers/endpoints exclusivos; preservar modelos/workers compartilhados.
2. **Rotas antigas** — não manter redirect permanente; rota some e ProtectedRoute/router não as registra. Bookmarks admin caem no fallback normal do SPA.
3. **Supply distribution** — remover endpoint + serviço + testes dedicados; manter `glassnode_service` e métricas usadas por mining/exchange-flows.
4. **Nav admin** — `adminOnlyLabels` E2E passa a esperar só itens admin restantes (`Combo`, `Backfill`, etc.).
5. **Spec backend** — REMOVED Requirement de supply distribution registered.

## Risks / Trade-offs

- **Risco**: confundir `components/signals/*` com `SignalHistoryPanel` / `lib/signalHistory.ts` do Monitor → mitigação: checklist explícito de preservação nos tasks.
- **Risco**: testes de nav admin/visual quebrarem após remoção de links → atualizar E2E e baselines se necessário.
- **Trade-off**: deixar `signal_monitor`/AI dashboard no código reduz blast radius agora, mas deixa dívida técnica residual.
