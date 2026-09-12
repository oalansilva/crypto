# Tasks — card-906-discovery-metrics-grid

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Grelha Acompanhar

- [x] 1.1 — Parciais top-5: thead e células ganham Sharpe, Win% e CAGR depois de Trades/cobertura, sem tirar Calmar / Max DD / Trades. Valores via `fmtNum` / `fmtPct(cagr)`. Fidelidade ao proto.
- [x] 1.2 — Linha com Calmar N/A (não finito / teto): Sharpe, Win% e CAGR também N/A quando o payload não tem valor finito.

## 2. Grelha Decidir

- [x] 2.1 — Leaderboard: as mesmas seis colunas no mesmo sítio, visíveis sem «+ detalhes». CAGR = `fmtPct(row.cagr)` (Retorno CAGR do promover), não Return de Favoritos.
- [x] 2.2 — `eligibility=insufficient_sample`: Sharpe, Win% e CAGR = N/A, como Calmar / Max DD / Trades. Sem Promover.
- [x] 2.3 — «+ detalhes» guarda B&H, Δ B&H, PF, mercado e janela; não é o único sítio de Sharpe/Win%/CAGR. Ordenar permanece Calmar e CAGR vs B&H.

## 3. Largura e estreito

- [x] 3.1 — Desktop: overflow-x na grelha; `min-width` da `.discovery-table` acomodando 6 números (P3). Ação continua à esquerda; CAGR no Acompanhar permanece numérico à direita (não herdar `th:last-child` left).
- [x] 3.2 — Mobile ≤720px: cards com `data-label` nas seis métricas; nenhuma nova coluna só atrás de «+ detalhes».

## 4. Verificação

- [x] 4.1 — Testes: Acompanhar e Decidir mostram as seis colunas; insuficiente N/A nas três novas; sort sem Sharpe/Win%/CAGR; Montar e Favoritos sem regressão. Playwright `/combo/discovery` desktop+mobile contra o proto.
- [x] 4.2 — `openspec verify` desta change.
