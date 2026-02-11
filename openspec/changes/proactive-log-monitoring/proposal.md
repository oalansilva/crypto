# Change Proposal: proactive-log-monitoring

## Why
Hoje, erros de execução (ex.: intervalo inválido no Binance) só aparecem quando o usuário reclama. Isso atrasa correções e causa fricção no fluxo do Lab. O objetivo é que o agente/dev detecte **e corrija proativamente** erros comuns, sem depender de intervenção manual.

## What Changes
- Detectar erros críticos de execução (ex.: intervalo inválido, símbolo inválido, falha de download) e gerar um diagnóstico estruturado.
- Aplicar correções automáticas quando possível (ex.: normalizar `4H` → `4h`, `BTC/USDT` → `BTCUSDT` para exchange).
- Quando não for possível auto‑corrigir, registrar recomendação clara para o usuário.
- Expor `diagnostic` na resposta do run (API) e persistir no log.
