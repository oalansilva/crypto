# Change Proposal: resilient-async-backtest

## Why
Hoje o backtest síncrono pode travar o fluxo principal quando há erro de execução. Queremos que o **Dev** consiga iniciar o backtest de forma assíncrona, observar falhas e continuar o loop de ajustes sem bloquear o sistema.

## What Changes
- Tornar a execução do backtest assíncrona na etapa Dev (disparar job e retornar imediatamente).
- Registrar erros de job de forma estruturada e permitir re‑tentativas no loop Dev ("Dev: ajusta template/motor" → "Dev: roda backtest via sistema").
- Garantir que o run mantenha estado consistente mesmo quando o job falha.
