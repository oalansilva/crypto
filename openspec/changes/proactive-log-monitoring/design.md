# Design: Proactive Runtime Error Detection & Auto-Correction

## Overview
Adicionar normalização proativa (timeframe/símbolo) antes do download e um classificador de erro para capturar falhas remanescentes. O diagnóstico será persistido no run e exposto via API.

## Components
- **InputNormalizer**: normaliza `timeframe` (ex.: `4H` -> `4h`) e `symbol` (ex.: `BTC/USDT` -> `BTCUSDT`).
- **ErrorClassifier**: mapeia mensagens/exception types para `diagnostic.type`.
- **RunLogger**: inclui o campo `diagnostic` nos logs de run.
- **Lab API**: retorna `diagnostic` no endpoint de run.

## Flow
1. Antes do download, InputNormalizer corrige `timeframe` e `symbol`.
2. Se ainda falhar, ErrorClassifier gera `{type, message, details}`.
3. RunLogger salva o diagnóstico no JSON do run.
4. `/api/lab/runs/{run_id}` retorna `diagnostic`.

## Error Types (MVP)
- `invalid_interval` (ex.: "Invalid interval", "interval=4H")
- `invalid_symbol`
- `download_error`

## Open Questions
- Expor `details` completo na API ou só em logs?
