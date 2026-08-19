## Context

O leaderboard de Discovery (`/combo/discovery`) persiste `DiscoveryResult` a partir de `run_combination` → `ComboOptimizer.run_optimization(..., deep_backtest=True)` **sem** `split_train_ratio`. A spec `discovery-leaderboard` exige CAGR, Calmar, benchmark B&H e delta vs B&H derivados do optimizer.

Hoje, em `combo_optimizer.py`, o enriquecimento de `cagr`, `calmar_ratio` e `benchmark` ocorre apenas dentro do bloco walk-forward (`split_train_ratio is not None`), nas linhas ~2175–2204 (IS/treino) e ~2139–2166 (OOS/holdout). O path legado (período inteiro, discovery) termina o backtest final com `_metrics_from_trades` + `_calculate_heavy_metrics`, que **não** produzem essas chaves.

`discovery_tasks.py` já mapeia corretamente `best_metrics["cagr"]`, `["calmar_ratio"]` e `["benchmark"]["cagr"]` para colunas `DiscoveryResult` — o bug é upstream, no optimizer.

Evidência DEV (card #599, sweep `94aa741b…`): MACD ETH 1d com 22 trades mostra Calmar/CAGR/Δ B&H = N/A; RSI scalping 1d com 0 trades mostra Sharpe/PF/win rate = 0 (correto para essas métricas) mas ranking metrics também N/A (correto) — porém MACD deveria ter ranking preenchido.

## Goals / Non-Goals

**Goals:**

- Após backtest final no path **sem** walk-forward split, calcular e anexar a `best_metrics`: `cagr`, `calmar_ratio`, `benchmark` (dict com `cagr` etc.) usando a mesma lógica do bloco IS existente.
- Usar trades do backtest final e série `close` de `df_final` (janela efetiva).
- Com **0 trades**: omitir ou definir `null` para métricas de ranking — **não** persistir `0.0` como CAGR/Calmar/benchmark.
- Testes automatizados no path discovery (`run_combination` ou helper extraído).
- Smoke manual em DEV: sweep com MACD ETH 1d exibe métricas de ranking preenchidas.

**Non-Goals:**

- Alterar walk-forward gate (#470/#503) nem critérios GO/NO-GO.
- Mudanças de UI obrigatórias (`UI impact: none`).
- P2 opcional (preflight warn scalping + 1d ou tooltip zero trades) — follow-up separado se não couber no mesmo PR.
- Reprocessar sweeps históricos em massa (dados antigos permanecem até novo sweep).

## Decisions

1. **Extrair helper reutilizável** `_enrich_ranking_metrics(trades, close_series, metrics_dict, *, legacy_zero_trade_ranking: bool = False) -> None` a partir do bloco IS walk-forward (~2175–2204).
   - Path **discovery** (`split_train_ratio is None`): chamar após `_calculate_heavy_metrics` com `legacy_zero_trade_ranking=False`.
   - Bloco **IS walk-forward**: chamar com `legacy_zero_trade_ranking=True` para preservar comportamento atual (`cagr=0.0` + benchmark calculado mesmo com 0 trades) até card dedicado de higiene walk-forward.
   - *Alternativa rejeitada:* passar `split_train_ratio=0.7` no discovery — mudaria semântica (treino/holdout) e violaria expectativa de janela completa no leaderboard.
   - *Alternativa rejeitada:* duplicar lógica inline só no discovery_tasks — duplicaria equity/CAGR já centralizado no optimizer.

2. **Sem trades → omitir chaves (discovery), não zero.** Com `legacy_zero_trade_ranking=False`, o helper só adiciona `cagr`/`calmar_ratio`/`benchmark` quando `len(trades) > 0` e valores finitos. **Proibido** gravar `cagr: None` ou `benchmark: {"cagr": None}` — chaves ausentes viram `N/A` em `discovery_tasks.py` via `.get()`. Isso evita regressão em `evaluate_go_nogo`, que trata chave omitida como default seguro, mas falharia com `None` explícito.
   - Com `legacy_zero_trade_ranking=True` (IS walk-forward), manter semântica legada de 0 trades.
   - Sharpe/PF/win rate continuam com semântica atual de `_metrics_from_trades` (0 quando sem trades).
   - Alinha com spec: *"Missing/non-finite values SHALL be N/A, never zero"* para métricas de ranking no path discovery.

3. **Equity curve:** reconstruir série de capital a partir dos trades ordenados por `entry_time` (mesmo padrão do bloco IS: capital inicial 100, multiplicativo por `profit`).

4. **Benchmark B&H:** `calculate_buy_and_hold(close_series, 100.0)` sobre `df_final["close"]` — mesma janela/candles do backtest final.

5. **Delta:** permanece calculado em `discovery_tasks.py` como hoje (`cagr - benchmark_cagr`, em pontos percentuais ×100) — sem mudança de contrato.

## Risks / Trade-offs

- **[Risco] Regressão no path walk-forward** → Helper compartilhado; refatorar bloco IS para chamar o mesmo helper; testes existentes de combo optimizer/walk-forward devem permanecer verdes.
- **[Risco] CAGR 0.0 legado no bloco IS com 0 trades** → Mitigado via flag `legacy_zero_trade_ranking=True` no IS; discovery usa `False` (omitir chaves).
- **[Risco] `None` explícito no dict quebra gate walk-forward** → Helper nunca grava `None`; só adiciona chaves com valores finitos ou omite (discovery 0-trade).
- **[Limitação conhecida] CAGR estratégia vs B&H** → Equity reconstruída por trade vs B&H por calendário de candles — comportamento herdado do bloco IS; fora do escopo deste card.
- **[Trade-off] Sweeps antigos** → Resultados já persistidos não são backfilled; admin precisa reexecutar sweep para ver métricas corrigidas.

## Migration Plan

1. Deploy backend DEV com fix.
2. Reiniciar worker discovery DEV (`criptofarol-dev-discovery-worker`).
3. Smoke: novo sweep ou combinação MACD ETH 1d — validar colunas Calmar/CAGR/Δ B&H no leaderboard.
4. Rollback: revert do commit; sweeps novos voltam ao comportamento anterior (N/A).

## Open Questions

- Nenhum bloqueante. P2 scalping+1d fica como follow-up opcional (#599 item 2).

## UI impact

`none` — correção backend-only. O leaderboard já renderiza N/A vs valores finitos; nenhuma superfície visual nova ou alteração de layout/copy obrigatória.

## Impeccable Brief

`N/A` — `UI impact: none`; correção de persistência de métricas no optimizer/discovery. Sem protótipo HTML nem redesign.

## Prototype

`N/A` — bug de dados/métricas no backend. Validação via testes automatizados + smoke no leaderboard DEV existente (`/combo/discovery`). Nenhuma tela nova ou delta visual.

## Impeccable Critique

`N/A` — sem superfície UI afetada.

## Impeccable Audit

`N/A` — sem superfície UI afetada.

## Impeccable Trace

`N/A` — card backend-only; evidência de design = testes + smoke DEV documentados em tasks.md.

## Prototype Validation

`N/A` — sem protótipo HTML. Smoke pós-implementação: leaderboard DEV com combinação com trades > 0.

## Design Critique

**Crítica isolada** (Task inherit, read-only) — card #599, change `fix-discovery-leaderboard-metrics`.

### Achados e disposição

| Dimensão | Achado | Severidade | Disposição |
|----------|--------|------------|------------|
| Produto | Problema/valor claros; P2 scalping+1d isolado | — | OK |
| Escopo | Tensão null-only vs IS legado | P1 | **Resolvido:** flag `legacy_zero_trade_ranking` |
| Riscos | `None` explícito vs chave omitida | P1 | **Resolvido:** contrato documentado em Decisions §2 |
| Riscos | Regressão walk-forward | P2 | Testes nomeados em tasks.md §2.3 |
| Spec | Delta alinhada à main spec | — | OK |
| Testes | Plano helper + discovery persist | — | OK |
| UI | `none` confirmado; leaderboard já formata N/A | — | OK |

### Riscos aceitos (P2, não bloqueantes)

- Sweeps históricos permanecem N/A até reexecução.
- OOS/holdout legado com `oos_cagr=0.0` em 0 trades — fora do escopo.
- CAGR assimétrico trade-equity vs calendário B&H — débito herdado.

### Referências avaliadas

- OpenSpec: `proposal.md`, `design.md`, `specs/discovery-leaderboard/spec.md`, `tasks.md`
- Main spec: `openspec/specs/discovery-leaderboard/spec.md`
- Código: `combo_optimizer.py` (IS ~2175–2204), `discovery_tasks.py` (`run_combination`)
- Prototype: **N/A** (backend-only)

**Design Agent verdict: PASS**
