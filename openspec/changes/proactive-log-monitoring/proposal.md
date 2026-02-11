# Change Proposal: proactive-log-monitoring

## Why
Hoje, erros de execução (ex.: intervalo inválido no Binance) só aparecem quando o usuário reclama. Isso atrasa correções e causa fricção no fluxo do Lab. O objetivo é que o **agente Dev** detecte e corrija proativamente erros comuns **durante a etapa Dev** (antes do backtest), sem depender de intervenção manual.

## What Changes
- Inserir uma etapa de **auto‑correção no fluxo do Dev** (entre receber strategy_draft e rodar o backtest) para normalizar inputs comuns.
- Aplicar correções automáticas quando possível (ex.: `4H` → `4h`, `BTC/USDT` → `BTCUSDT` para exchange) **antes** da execução.
- Quando não for possível auto‑corrigir, registrar um diagnóstico e sugestão clara para o usuário.
- Expor `diagnostic` na resposta do run (API) e persistir no log.
