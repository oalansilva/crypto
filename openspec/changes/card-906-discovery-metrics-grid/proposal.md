## Why

O operador na Descoberta não consegue ler na grelha os números fáceis que já vê em Favoritos (Sharpe, Win%, retorno): no Decidir eles só aparecem depois de «+ detalhes»; no Acompanhar nem isso. Comparar candidatos vira abrir linha a linha. Q1=A e Q2=A estão travadas: CAGR anualizado da varredura (não Return acumulado) e o mesmo conjunto de colunas nos dois modos.

## What Changes

- Nas parciais do Acompanhar (top-5) e na lista do Decidir, a grelha mostra em coluna, sem expandir a linha: Calmar, Max DD, Trades/cobertura, Sharpe, Win% e CAGR.
- CAGR é o retorno anualizado da varredura (o mesmo «Retorno (CAGR)» do diálogo de promover), não o Return acumulado de Favoritos.
- Linha «Amostra insuficiente» no Decidir: Sharpe, Win% e CAGR também mostram N/A, como Calmar / Max DD / Trades já fazem.
- As duas grelhas usam o mesmo conjunto de colunas no mesmo sítio.
- «+ detalhes» no Decidir deixa de ser o único sítio de Sharpe / Win% / CAGR; guarda B&H, Δ B&H, PF, mercado e janela.

Fora: grelha de Favoritos; modo Montar (sem delta de colunas); motor/ranking/selo GO/NO-GO/promoção; ordenar por Sharpe/Win%/CAGR; Return acumulado; tirar Calmar / Max DD / Trades/cobertura; só um dos modos.

## Capabilities

### New Capabilities

- (nenhuma) — o comportamento entra nas capacidades já existentes da Descoberta.

### Modified Capabilities

- `discovery-leaderboard`: Sharpe, Win% e CAGR passam a colunas visíveis na lista do Decidir, junto com Calmar, Max DD e Trades/cobertura; amostra insuficiente pinta N/A nas três novas; ordenação continua só Calmar e CAGR vs B&H; «+ detalhes» deixa de ser o único sítio dessas três métricas.
- `discovery-three-modes`: parciais top-5 do Acompanhar usam o mesmo conjunto de seis colunas de métrica; Montar permanece sem grelha de candidatos e sem delta deste card.

## Impact

- Frontend: `DiscoveryPage.tsx` / `DiscoveryPage.css` — thead e células das parciais e do leaderboard; `fmtNum` / `fmtPct` já existentes; overflow-x e cards mobile com `data-label`.
- API/backend: sem cálculo novo; payload já expõe `sharpe_ratio`, `win_rate`, `cagr`.
- Specs canónicas: `openspec/specs/discovery-leaderboard`, `discovery-three-modes`.
- Protótipo: `frontend/public/prototypes/card-906-discovery-metrics-grid/`.
- Sem mudança em Favoritos, promover, motor, selo GO/NO-GO ou opções de ordenar.
