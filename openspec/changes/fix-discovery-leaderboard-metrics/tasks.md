## 1. Refatorar cálculo de métricas de ranking no optimizer

- [x] 1.1 Extrair helper `_enrich_ranking_metrics(..., *, legacy_zero_trade_ranking=False)` de `combo_optimizer.py` a partir do bloco IS walk-forward (~2175–2204)
- [x] 1.2 Refatorar bloco IS walk-forward para usar o helper com `legacy_zero_trade_ranking=True` (preservar comportamento legado)
- [x] 1.3 Invocar helper após backtest final quando `split_train_ratio is None` com `legacy_zero_trade_ranking=False`, usando `trades` e `df_final["close"]`
- [x] 1.4 Garantir que path discovery com 0 trades **omite** chaves `cagr`, `calmar_ratio`, `benchmark` (nunca `0.0` nem `None` explícito)

## 2. Testes

- [x] 2.1 Teste unitário do helper: trades > 0 → métricas finitas; 0 trades → chaves ausentes/null
- [x] 2.2 Teste de integração ou unitário em `run_combination` (mock optimizer) verificando persistência de `cagr`, `calmar_ratio`, `benchmark_cagr`, `delta_cagr_vs_bh` no `DiscoveryResult`
- [x] 2.3 Rodar testes focados: `pytest backend/tests/unit/test_discovery_celery_tasks.py` + novos arquivos
- [x] 2.4 Regressão walk-forward pós-refator: `pytest backend/tests/unit/test_combo_optimizer_final_execution_mode.py backend/tests/unit/test_walk_forward_combined_gate.py`

## 3. Validação

- [x] 3.1 `openspec status --change fix-discovery-leaderboard-metrics` (4/4 artifacts complete)
- [ ] 3.2 Smoke DEV documentado: sweep/combinação MACD ETH 1d com trades > 0 exibe Calmar, CAGR, B&H e Δ B&H no leaderboard (não N/A) — pendente após merge/restart worker

## 4. Fora de escopo (P2 opcional — follow-up)

- [ ] 4.1 Preflight warn ou tooltip para scalping em 1d com zero sinais — **não bloqueia Done deste card**
