## 1. Invocação e persistência Discovery

- [x] 1.1 Em `run_combination`, passar `split_train_ratio=0.7` junto com `deep_backtest=True`
- [x] 1.2 Mesclar no JSON `metrics`: `split_train_ratio=0.7`, `split_applied`, `oos_metrics` e `oos_verdict` (incluir `status=ERROR` quando devolvido)
- [x] 1.3 Sanitizar ranking no worker: `trades_count==0` ou valor não finito → `cagr`/`calmar_ratio`/`benchmark_cagr`/`delta_cagr_vs_bh` null (nunca persistir `0.0` do helper IS legado)
- [x] 1.4 Se `trades_count>0` e `cagr` ausente/não finito após o optimizer (holdout ERROR), chamar `_enrich_ranking_metrics(..., legacy_zero_trade_ranking=False)` no worker e persistir IS
- [x] 1.5 `start_at`/`end_at`/`expected_candles`/`coverage`/`trades_count` e elegibilidade 30/90 usam a janela IS (candles do backtest final)

## 2. Testes

- [x] 2.1 Chamada `run_optimization` com `deep_backtest=True` e `split_train_ratio=0.7`
- [x] 2.2 Persistência: `metrics.split_train_ratio=0.7` e OOS quando o mock devolver; ranking IS finito com trades > 0
- [x] 2.3 Zero trades IS com `best_metrics.cagr=0.0` → colunas de ranking null; NO-GO OOS não altera `eligibility`
- [x] 2.4 Holdout `ERROR` + trades IS sem `cagr` no retorno → ranking IS preenchido pelo worker; `oos_verdict` persistido
- [x] 2.5 Coverage/`start_at`/`end_at` derivados dos candles IS (não da janela do snapshot do sweep)
- [x] 2.6 Regressão: helper `#599` `legacy_zero_trade_ranking=False` e testes walk-forward Combo existentes permanecem verdes

## 3. Validação

- [x] 3.1 `openspec status --change discovery-walk-forward-split` completo; specs da change validam
- [ ] 3.2 Smoke DEV após merge/restart worker: logs `Walk-forward split` 70/30 + Deep 15m; leaderboard com métricas IS quando houver trades; 0 trades → N/A
