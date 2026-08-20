## Why

O Discovery em DEV otimiza com Deep Backtest 15m, mas **sem** walk-forward. Alan, ao testar o #599, pediu que cada combinação use as mesmas opções da tela Combo: Deep Backtest (15m Precision) e Validação walk-forward (split 70/30). O #599 permanece `Done`; o design daquele card rejeitou o split. Este card (#605) é o requisito novo.

## What Changes

- `run_combination` passa `deep_backtest=True` e `split_train_ratio=0.7` em `ComboOptimizer.run_optimization`.
- Ranking do leaderboard (CAGR, Calmar, B&H, Δ B&H, Sharpe, PF, trades) passa a refletir o **treino (IS, 70% mais antigo)**, não a janela inteira.
- O resultado persiste evidência do split (`split_train_ratio`, `oos_metrics`, `oos_verdict`) no JSON `metrics` já existente — sem coluna nova nem UI nova.
- Com 0 trades no IS, métricas de ranking permanecem N/A (null), não zeros disfarçados.
- Testes da chamada discovery com split 70/30; smoke DEV em novo sweep/combinação.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `discovery-sweep`: cada combinação SHALL invocar o optimizer com Deep Backtest 15m e walk-forward `split_train_ratio=0.7`.
- `discovery-leaderboard`: ranking e janela efetiva SHALL ser o treino (IS); coverage 90% e mínimo de 30 trades medem essa janela IS; evidência do holdout no JSON; a requirement do #599 (path Discovery sem split) é removida/substituída.

## Impact

- `backend/app/tasks/discovery_tasks.py` — passar `split_train_ratio=0.7`; sanitizar ranking N/A; anexar OOS/`split_applied` ao JSON `metrics`; se CAGR IS faltar após holdout ERROR, enriquecer no worker com `_enrich_ranking_metrics(..., legacy_zero_trade_ranking=False)`.
- `backend/app/services/combo_optimizer.py` — sem mudança da lógica de split (#470); o worker não depende do helper IS legado (`cagr=0.0`).
- `backend/tests/` — invocação 70/30, persistência IS/OOS, 0 trades com `cagr=0.0` → null, holdout ERROR com trades IS, coverage da janela IS.
- Worker discovery DEV (`criptofarol-dev-discovery-worker`) precisa do código novo após merge.
- Sem mudança de API pública, sem toggle na UI de Discovery (`UI impact: none`).
- Card GitHub #605 (filho do #599).
- Sweeps históricos não são reprocessados.
