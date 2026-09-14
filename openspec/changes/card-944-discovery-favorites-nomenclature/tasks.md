# Tasks — card-944-discovery-favorites-nomenclature

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Grelha Acompanhar

- [x] 1.1 — Parciais top-5: thead e células na ordem Sharpe → Trades → Win% → Return → Max DD → Calmar → CAGR anualizado. Sem «+ detalhes». Fidelidade ao proto.
- [x] 1.2 — Cabeçalho Trades (não Trades/cobertura); cobertura só como subtexto. Return visível; CAGR anualizado no final.

## 2. Grelha Decidir

- [x] 2.1 — Leaderboard: as mesmas sete colunas no mesmo sítio, visíveis sem «+ detalhes». Return = composto da janela (`total_return` / `total_return_pct`); CAGR anualizado = `fmtPct(row.cagr)`.
- [x] 2.2 — `eligibility=insufficient_sample`: Sharpe, Trades, Win%, Return, Max DD, Calmar e CAGR anualizado = N/A. Sem Promover.
- [x] 2.3 — «+ detalhes» guarda B&H, Δ B&H, PF, mercado e janela. Ordenar permanece Calmar e CAGR vs B&H.

## 3. Payload e largura

- [x] 3.1 — Expor `total_return` / `total_return_pct` no payload da grelha se o top-level ainda não os envia (P3; ler o JSON persistido). N/A se ausente. Sem schema novo.
- [x] 3.2 — Desktop: overflow-x; `min-width` da `.discovery-table` acomodando 7 métricas (P3). Mobile ≤720px: cards com `data-label` na nova ordem.

## 4. Fora e verificação

- [x] 4.1 — Montar sem delta de colunas. Favoritos sem mudança. Ranking, filtros, GO/NO-GO, promover (#897) intactos.
- [x] 4.2 — Testes: as duas grelhas na nova ordem; Return ≠ CAGR; insuficiente N/A no Return; sort sem Sharpe/Win%/Return/CAGR anualizado; Montar e Favoritos sem regressão. Playwright `/combo/discovery` desktop+mobile contra o proto.
- [x] 4.3 — `openspec verify` desta change.
