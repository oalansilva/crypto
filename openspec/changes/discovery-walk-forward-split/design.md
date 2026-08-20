## Context

Card #605 (filho do #599). Alan testando Discovery em DEV pediu que cada combinação use as mesmas opções da tela Combo: **Deep Backtest (15m Precision)** e **Validação walk-forward (split 70/30)**.

Estado atual (`develop`):

- `discovery_tasks.run_combination` chama `ComboOptimizer.run_optimization(..., deep_backtest=True)` **sem** `split_train_ratio`.
- `ComboOptimizer` já implementa walk-forward quando `split_train_ratio` é informado (card #470): otimização no treino (70% mais antigo), backtest final no treino, holdout 30% com `oos_metrics` / `oos_verdict`.
- No path **com** split, o enriquecimento CAGR/Calmar IS usa `legacy_zero_trade_ranking=True` **dentro** do `try` do holdout: 0 trades grava `cagr=0.0`; holdout `ERROR` pode omitir CAGR IS mesmo com trades.
- O #599 (`Status=Done`) preenche ranking no path **sem** split. Esse path deixa de ser o caminho Discovery. A change ativa `fix-discovery-leaderboard-metrics` ainda ADDED “without walk-forward split”; este card REMOVE essa requirement para o archive do lote não contradizer.

`UI impact: none` — backend/worker; o leaderboard já renderiza as colunas de ranking. Sem toggle, badge ou tela nova neste card.

## Goals / Non-Goals

**Goals:**

- Toda combinação Discovery invoca o optimizer com `deep_backtest=True` e `split_train_ratio=0.7`.
- Colunas de ranking do `DiscoveryResult` (CAGR, Calmar, B&H, Δ, Sharpe, PF, trades) vêm do **treino (IS)**.
- Janela efetiva persistida (`start_at`/`end_at`/`expected_candles`/`coverage`/`trades_count`) **é o treino**; elegibilidade 30 trades / 90% coverage mede essa janela IS, não o snapshot 6m/2y do sweep.
- JSON `metrics` persiste `split_train_ratio`, `split_applied`, `oos_metrics` e `oos_verdict` (incluindo `status=ERROR`).
- 0 trades no IS → ranking N/A (null), **mesmo se** o optimizer devolver `cagr=0.0`.
- Se o holdout falhar e o IS tiver trades mas `cagr` ausente, o worker enriquece ranking no próprio `run_combination`.
- Testes da invocação + persistência + sanitização; smoke DEV após `Pronto para Dev`/merge.

**Non-Goals:**

- Reabrir ou regredir o #599 (status `Done` permanece).
- Redesign do leaderboard, toggle/badge/copy na UI de Discovery.
- Mudar critérios GO/NO-GO da Combo (#470/#503). O gate walk-forward (100 trades IS / Sharpe 0.8) **não** é o gate de elegibilidade Discovery.
- Bloquear ranking/promoção Discovery por `oos_verdict=NO-GO` neste card.
- Reprocessar sweeps históricos.
- Refatorar o bloco walk-forward do `ComboOptimizer` (helper legado IS `cagr=0.0` fica; o worker sanitiza).

## Decisions

1. **Ativar o split na chamada Discovery, não reimplementar walk-forward.**
   - `run_combination(..., split_train_ratio=0.7)`.
   - *Alternativa rejeitada:* ranking na janela inteira **e** holdout à parte.
   - *Alternativa rejeitada no #599:* path sem split. Superada pelo #605.

2. **Ranking = IS, sanitizado no worker.**
   - Trades/candles do resultado do optimizer são do treino quando o split aplica.
   - Após `run_optimization`, o worker:
     1. se `len(trades)==0` ou valor não finito: persistir `cagr`/`calmar_ratio`/`benchmark_cagr`/`delta_cagr_vs_bh` como **null** (nunca `0.0`);
     2. se `len(trades)>0` e `cagr` ausente/não finito: chamar `_enrich_ranking_metrics(trades, close_IS, metrics, legacy_zero_trade_ranking=False)` e então mapear;
     3. `float(cagr)` só quando finito e `trades>0`.
   - *Não* alterar o helper IS legado do ComboOptimizer neste card.

3. **OOS no JSON `metrics`, sem migration.**
   - Mesclar `split_train_ratio=0.7`, `split_applied` (true se o resultado trouxer `oos_verdict` ou `oos_metrics`; false se o optimizer skipou o split), `oos_metrics`, `oos_verdict` (inclui `{status: ERROR, ...}`).
   - Omitir `oos_*` só quando ambos forem `None` e `split_applied=false`.
   - Leaderboard não lê OOS neste card.
   - Gate Combo **não** altera `eligibility` Discovery.

4. **Janela efetiva = treino (IS).**
   - `start_at`/`end_at`/`expected_candles`/`observed_valid_candles`/`coverage`/`trades_count` usam os candles do backtest final (treino).
   - Elegibilidade: ≥30 trades **IS** e ≥90% coverage da **janela IS**, não da janela pedida no snapshot do sweep.
   - Trades: mais conservador (70% da história). Coverage: **mais permissivo** se medida no treino (denominador encolhe); **não** é “coverage mais conservadora”.
   - *Alternativa rejeitada neste card:* coverage da janela 6m/2y com só candles IS (~70% → quase tudo `Baixa amostra`). Follow-up se Alan quiser o denominador do sweep.

5. **Deep Backtest permanece `True`.** Fonte `ccxt`. Deep 15m no IS ainda recebe `since`/`until` da janela cheia (herança Combo; P2 aceito).

6. **Constantes.** Ratio fixo `0.7`. Sem flag de ambiente.

7. **Supersede OpenSpec do #599.** Este delta REMOVE a requirement “Discovery optimizer path SHALL persist ranking metrics without walk-forward split”. Archive do lote: #599 não deixa o spec principal exigindo path sem split.

## Risks / Trade-offs

- **[Risco] Menos trades IS → mais `Baixa amostra`.** Esperado; não relaxar o mínimo 30.
- **[Risco] Coverage no IS é mais permissiva** (90% do treino, não do sweep). Mitigação: contrato na spec MODIFIED; follow-up se Alan quiser denominador do snapshot.
- **[Risco] NO-GO no holdout ainda pode rankear/promover.** Aceito; evidência no JSON.
- **[Risco] Holdout ERROR.** Mitigação: worker enriquece IS; persiste `oos_verdict=ERROR`.
- **[Risco] Split skip (`<2` candles).** Raro em 6m/2y; gravar `split_applied=false` e ainda `split_train_ratio=0.7` pedido. Não mentir que o holdout rodou.
- **[Risco] Change #599 ainda ativa.** Mitigação: REMOVED neste delta.
- **[Risco] Sweep mais lento.** Um backtest OOS por combinação; aceitável.
- **[Trade-off] Sweeps antigos** sem split até novo sweep.
- **[P2] Deep 15m IS com since/until da janela cheia** — herança Combo; fora de refator neste card.

## Migration Plan

1. Após `Pronto para Dev`: implementar na branch `card-605-discovery-walk-forward-split`.
2. Merge em `develop`, `./restart`, reiniciar `criptofarol-dev-discovery-worker`.
3. Smoke: logs `Walk-forward split: train=… (70%)`; ranking IS com trades; 0 trades → N/A.
4. Rollback: reverter o commit; Discovery volta ao path sem split (#599).

## Open Questions

Nenhum bloqueante. Gate de promoção por `oos_verdict` e coverage na janela do sweep ficam como follow-up se Alan pedir.

## UI impact

`none` — invocação do optimizer no worker. Nenhuma superfície visual nova; as colunas existentes passam a mostrar IS.

## Impeccable Brief

`N/A` — `UI impact: none`; sem protótipo HTML nem redesign.

## Prototype

`N/A` — backend/worker. Validação via testes + smoke DEV em `/combo/discovery`. Sem tela nova ou delta visual.

## Impeccable Critique

`N/A` — sem superfície UI afetada.

## Impeccable Audit

`N/A` — sem superfície UI afetada.

## Impeccable Trace

`N/A` — card backend-only.

## Prototype Validation

`N/A` — sem protótipo HTML.

## Design Critique

**Crítica 1** ([BLOCKED](4b12d927-0aa1-4632-bb83-c5ba5bb0c72f)): P1 — N/A vs `cagr=0.0` do helper IS; coverage/janela sem MODIFIED; requirement #599 sem REMOVE.

**Resolução:** Decisões 2, 4 e 7; deltas MODIFIED/REMOVED; tasks 1.3–1.5 e 2.3–2.6.

**Crítica 2** (Task inherit, read-only, [PASS](1c92f567-f954-4100-a842-f5c86a5c131c)) — re-leitura dos cinco artefatos após o must-fix.

| Dimensão | Achado | Severidade | Disposição |
|----------|--------|------------|------------|
| BLOCKED-1 N/A / enrich | Worker sanitiza `0.0`; holdout ERROR enriquece IS | — | Corrigido |
| BLOCKED-2 janela | Evidence window = IS; coverage permissiva, não conservadora | — | Corrigido |
| BLOCKED-3 #599 | REMOVED da requirement sem split | — | Corrigido |
| Produto / UI / escopo | Deep 15m + WF 70/30; Prototype N/A | — | OK |
| Archive lote | Ordem #599 × #605 para o REMOVE valer no spec principal | P2 | Aceito |
| NO-GO promove / Deep 15m janela cheia / sem badge IS | Herança/non-goal | P2 | Aceito |

**Design Agent verdict: PASS**
