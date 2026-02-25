# Design: Iterative Dev Loop

## Overview
Adicionar um loop de ajuste no estágio Dev dentro de `_run_lab_autonomous_sync` (backend/app/routes/lab.py). O loop roda backtest, avalia preflight, aplica ajustes simples no template (relaxamento de filtros/indicadores mínimos) e re‑roda até sucesso ou limite.

## Flow (aligned with Alan’s diagram)
1. Trader cria `strategy_draft`.
2. Usuário aprova upstream.
3. Dev cria template custom.
4. Dev roda backtest.
5. Se resultado inválido → Dev ajusta template → volta ao backtest.
6. Se resultado OK → Trader valida.
7. Trader decide (aprovar/ajustar/rejeitar).

## Adjustment Strategy (MVP)
- **Se 0 trades ou métricas degeneradas:**
  - Remover exigência de *cross* explícito de EMA (trocar por `close > ema50` / `close < ema50`).
  - Relaxar faixa de RSI (ex.: 40–50 → 40–55).
  - Reduzir limiar de ADX (ex.: 20 → 15) quando existir.
  - Garantir **ATR** presente nos indicadores se stop/trailing usa ATR.
- Todas as alterações devem ser registradas em trace (`dev_adjustment_applied`).

## Preflight Criteria
Utilizar `*_metrics_preflight` existente como gate automático (holdout trades mínimos, sharpe mínimo). Quando falhar, entra no loop de ajuste.

## Limits
- Tentativas de ajuste: `max_dev_adjustments` (default 3; derivado de `max_iterations` ou novo campo futuro).

## Telemetry
- `dev_adjustment_applied` com: attempt, template, regras aplicadas.
- `dev_adjustment_skipped` quando não há ajustes disponíveis.
