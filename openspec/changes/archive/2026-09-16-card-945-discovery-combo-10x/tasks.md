# Tasks — card-945-discovery-combo-10x

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.
> Skills: `.cursor/skills/openspec-apply-change` no Apply; `design-critic` já correu no autor. Sem `/opsx:apply` em Design.

## 1. Chão e andar A (oráculo + fixtures + testes)

- [x] 1.1 Comentar no card `baseline-945=<sha de origin/develop>` no arranque do Apply
- [x] 1.2 Copiar literalmente o caminho actual para `backend/tests/oracles/card_945_legacy.py` (`calculate_indicators`, `_evaluate_logic_vectorized`, loop de `generate_signals`, `simulate_execution_with_15m`, `extract_trades_from_signals`, `_metrics_from_trades`) — só teste, não produto
- [x] 1.3 Gerar e commitar parquet congelado (≥ 2 símbolos, 1d + 15m) e `sha256` por coluna / lista de trades **antes** de qualquer mudança de produto
- [x] 1.4 Testes de golden verdes contra o código **actual**: indicadores (14 templates × 3 janelas × ≥ 50 params, `assert_array_equal` + sha256); máscaras; cache fria/quente + A→B→A + sem hit cruzado; trial (14 × long/short × ≥ 50, incl. stops extremos e `fast_1d`); vencedor/holdout/GO/NO-GO da representativa. Zero `allclose`
- [x] 1.5 Pin de `TA-Lib`, `numpy` e `pandas` no lock na versão do `pip freeze` do VPS; o relatório de golden regista essas versões
- [x] 1.6 Primeiro commit = **só** 1.2–1.5. Produto (`combo_optimizer.py`, `combo_strategy.py`, `deep_backtest.py`) intacto

## 2. Andar B — cache, janela e imutabilidade

- [x] 2.1 Cache por worker de indicadores + máscaras; chave = indicadores resolvidos + `entry_logic`/`exit_logic`/`derived_features` + janela (primeiro/último ts, `len`, hash OHLCV); `stop_loss` fora da chave
- [x] 2.2 Saída imutável (`copy()` / arrays só-leitura); mesma coerção `float64`/`NaN`; nenhum trial escreve no objecto cacheado
- [x] 2.3 Goldens de indicadores/máscaras/cache continuam verdes contra o oráculo do andar A (fixtures intocados)

## 3. Andar B — loop, sim 15m, fast_1d

- [x] 3.1 Loop de posição orientado a eventos com as mesmas comparações float (`(low - entry)/entry <= -stop`, open do candle seguinte, `i > 0`, stop > exit, `continue` após saída)
- [x] 3.2 Sim 15m numpy (`asi8`/`searchsorted`, sem `iterrows`, sem `df.copy()` por trial, timestamps ISO 1× por worker, coverage guard 1× por worker)
- [x] 3.3 Fallback `fast_1d` com o mesmo tratamento numpy e semântica idêntica
- [x] 3.4 Funções lentas permanecem no produto como `_legacy_*`. Mesmas chamadas `talib.*`; sem reescrever PnL/fee/stop/score/métricas; sem vectorizar `_metrics_from_trades`

## 4. Andar B — ordem, R2–R4, setup, interruptor

- [x] 4.1 Ordenar resultados por índice de batch/trial (ou tie-break por params) **antes** do score; empate exacto reproduz o mesmo vencedor
- [x] 4.2 R2–R4: submeter ao pool os batches dos branches da ronda em conjunto; `OUTBOX_MAX_PER_SWEEP=1`; selecção por ronda intacta
- [x] 4.3 Cortar setup (tail exchange / `check_intraday_availability`) só quando 1d+15m daquele par já estão no disco e cobrem o fim do período; preflight do sweep intacto
- [x] 4.4 `COMBO_OPTIMIZER_LEGACY=1` nos serviços do motor (varredura, laboratório, lote, revalidação / regenerar favorito) chama `_legacy_*` em **todas** essas telas; default sem a flag = caminho rápido
- [x] 4.5 Commits de velocidade **não** tocam oráculo nem fixtures. Sem squash A com B

## 5. Callers, prova de relógio, verificação

- [x] 5.1 Confirmar que laboratório, gerar em lote e revalidação / regenerar favorito não têm ramo lento paralelo — herdam o caminho rápido (e o interruptor)
- [x] 5.2 Evidência de relógio no **serviço DEV da Descoberta** (não nos testes): representativa ≤ 14,8 s e R1–R4 ≤ 11 s com velas já no disco; comentar journal no card. Testes automáticos = igualdade, nunca wall-clock
- [x] 5.3 Review: listar cada função reescrita ao lado da original; recusar diff de fórmula/`talib.*`/fixture sem justificativa; `git revert` de B aplica-se sem conflito com A; `baseline-945` no card
- [x] 5.4 MUST NOT: frontend/src, rotas, copy, proto HTML, grid/score/elegibilidade/ranking, paralelizar o sweep, force-push, apagar `_legacy_*`/oráculo
- [x] 5.5 `openspec validate --change "card-945-discovery-combo-10x"` e testes de golden verdes
