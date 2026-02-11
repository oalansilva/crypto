# Design: Proactive Log Monitoring

## Overview
Adicionar um classificador de erro que observe falhas de execução (especialmente download de OHLCV) e registre um diagnóstico estruturado no run. O diagnóstico será exposto via API para a UI e persistido em log.

## Components
- **ErrorClassifier**: função utilitária para mapear mensagens/exception types para um `diagnostic.type`.
- **RunLogger**: inclusão do campo `diagnostic` nos logs de run.
- **Lab API**: incluir `diagnostic` na resposta do endpoint de run.

## Flow
1. Execução falha ao baixar dados (ex.: ccxt BadRequest Invalid interval).
2. ErrorClassifier detecta e gera `{type, message, details}`.
3. RunLogger salva o diagnóstico no JSON do run.
4. `/api/lab/runs/{run_id}` retorna `diagnostic`.

## Error Types (MVP)
- `invalid_interval` (ex.: "Invalid interval", "interval=4H")
- `invalid_symbol`
- `download_error`

## Open Questions
- Expor `details` completo na API ou só em logs?
