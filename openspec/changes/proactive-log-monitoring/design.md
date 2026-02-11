# Design: Dev-Stage Proactive Error Correction

## Overview
Inserir uma etapa explícita no **Dev** para normalizar inputs antes do backtest (timeframe/símbolo) e um classificador de erro para capturar falhas remanescentes. O diagnóstico será persistido no run e exposto via API.

## Components
- **DevInputNormalizer**: normaliza `timeframe` (ex.: `4H` -> `4h`) e `symbol` (ex.: `BTC/USDT` -> `BTCUSDT`) no fluxo do Dev, antes do backtest.
- **ErrorClassifier**: mapeia mensagens/exception types para `diagnostic.type`.
- **RunLogger**: inclui o campo `diagnostic` nos logs de run.
- **Lab API**: retorna `diagnostic` no endpoint de run.

## Flow
1. Dev recebe `strategy_draft` e inputs.
2. DevInputNormalizer corrige `timeframe` e `symbol`.
3. Dev roda backtest com inputs normalizados.
4. Se falhar, ErrorClassifier gera `{type, message, details}`.
5. Dev ajusta template/motor com base no diagnóstico e tenta novamente.
6. RunLogger salva o diagnóstico no JSON do run.
7. `/api/lab/runs/{run_id}` retorna `diagnostic`.

## Error Types (MVP)
- `invalid_interval` (ex.: "Invalid interval", "interval=4H")
- `invalid_symbol`
- `download_error`

## Open Questions
- Expor `details` completo na API ou só em logs?
