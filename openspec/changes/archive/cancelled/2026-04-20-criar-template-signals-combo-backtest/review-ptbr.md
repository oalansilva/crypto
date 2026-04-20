# Review PT-BR: Template de Sinais para Backtesting no Combo

**Card:** #65  
**change_id:** `criar-template-signals-combo-backtest`  
**Estágio:** DESIGN

---

## O que é

Criar um template "RSI+MACD+Bollinger Signals" no sistema Combo existente que usa `_build_signal()` (Card #53) para fazer backtest histórico.

## Decisões-chave

| Item | Valor |
|------|-------|
| Template | "rsi_macd_bollinger_signals" |
| Reaproveita | `_build_signal` em binance_service.py |
| Período default | 365 dias |
| UI | Reaproveita `/combo/select`, `/combo/configure`, `/combo/results` |
| Métricas | win_rate, total_profit_pct, max_drawdown, avg_trade_duration |

## O que foi desenhado

### Backend
- **Template** criado no banco SQLite (combo_templates)
- **Schema** SignalsBacktestRequest/Response com Trade aninhado
- **Service** signals_backtest_service.py com:
  - Fetch de candles históricos
  - Iteração com `_build_signal()` em cada ponto (sem lookahead)
  - Simulação de entry/exit com target_price e stop_loss do sinal
  - Cálculo de métricas (win rate, profit, drawdown)
- **Endpoint** `POST /api/combos/signals-backtest`

### Frontend
- Configure exibe campos extras: asset, days, risk_profile, initial_capital
- Results reaproveita UI existente (já suporta trades array)

## Escopo

**Dentro:** Template, endpoint, backtest service, integração com UI existente.  
**Fora:** Otimização de parâmetros RSI/MACD/BB, sinais SELL para short, alertas.

## Fluxo

```
Select → Configure (param) → Backtest (signals) → Results (metrics+trades)
```

## Dependências

- Card #53 ✅ — `_build_signal` implementado
- Sistema Combo ✅ — select/configure/results existem

## Próximo passo

Passar para DEV para implementação do template, service e endpoint.
