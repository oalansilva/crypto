## Why

Varreduras de Discovery concluídas com sucesso persistem resultados no leaderboard com Calmar, CAGR, benchmark e Δ B&H sempre **N/A**, mesmo quando há trades fechados (ex.: MACD ETH 1d com 22 trades). A spec `discovery-leaderboard` já exige essas métricas; o fluxo discovery chama `ComboOptimizer.run_optimization` sem `split_train_ratio`, e o cálculo de CAGR/Calmar/benchmark só roda no bloco walk-forward — violação observada em DEV em 19/08/2026 (card #599).

## What Changes

- Extrair/reutilizar o cálculo de CAGR, Calmar e buy-and-hold benchmark já existente no bloco IS do walk-forward e aplicá-lo após o backtest final quando `split_train_ratio` for `None` (path discovery legado).
- Com **0 trades**, persistir `null`/`N/A` para métricas de ranking — nunca `0.0` disfarçado como valor computado.
- Testes unitários/integração cobrindo persistência de métricas no path `run_combination` → `DiscoveryResult`.
- **Opcional (P2, fora do escopo mínimo):** preflight warn ou tooltip para templates scalping em timeframe `1d` com zero sinais — follow-up se não couber no mesmo card.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `discovery-leaderboard`: explicitar que o path discovery (optimizer sem walk-forward split) SHALL produzir e persistir CAGR, Calmar, benchmark e delta vs B&H quando houver trades fechados; SHALL manter N/A quando não computável.

## Impact

- `backend/app/services/combo_optimizer.py` — enriquecer `best_metrics` após backtest final no path sem split.
- `backend/app/tasks/discovery_tasks.py` — sem mudança de contrato; passa a receber métricas preenchidas.
- `backend/tests/` — novos testes focados em métricas de ranking no discovery.
- Sem mudança de API pública nem de UI obrigatória (`UI impact: none`).
- Card GitHub #599.
