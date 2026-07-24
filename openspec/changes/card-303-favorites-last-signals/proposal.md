## Why

No Monitor, a mesma estratégia já mostra os últimos sinais confirmados. Em Favoritos, esses sinais não aparecem, forçando o trader a abrir o Monitor só para ver o histórico recente.

## What Changes

- Favoritos passa a carregar e preservar o `signal_history` do Monitor para a mesma estratégia/ativo/timeframe.
- A tela de resultados de Favoritos (ComboResults) exibe o painel de últimos sinais com a mesma semântica do Monitor.
- Sync lento/falho deixa de virar “sem sinais” silencioso: empty state ou erro explícito.
- Cobertura automatizada e visual do caso Monitor tem sinais → Favoritos também mostra.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `favorites`: exigir paridade dos últimos sinais do Monitor na análise de Favoritos.
- `monitor`: reutilizar o contrato público de `signal_history` como fonte canônica dos últimos sinais também em Favoritos.

## Impact

- Frontend: `FavoritesDashboard.tsx`, `ComboResultsPage.tsx`, possível extração compartilhada do painel de histórico de `ChartModal.tsx`.
- Backend: preferencialmente sem mudança de contrato; eventual ajuste só se o fetch por favorito for necessário.
- Testes: `favorites-view-results.spec.ts`, Playwright visual de Favoritos.
