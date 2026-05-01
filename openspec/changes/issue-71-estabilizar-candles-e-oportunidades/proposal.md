## Why

A estabilidade do fluxo de Monitor ainda quebra em cenários reais de beta:
algumas respostas de candles e oportunidades podem ficar lentas ou falhar de forma a bloquear a experiência no frontend.
Precisamos estabilizar sem alterar comportamento funcional do produto, focando em 4h/1d para candles e em resiliência de erros no monitoramento de estratégias.

## What Changes

- Garantir que `/api/market/candles` responda `4h` e `1d` de forma consistente para ambos os tipos de ativo.
- Melhorar a robustez de `/api/opportunities` para não depender de dados de uma única estratégia e para não bloquear por timeouts de coleta.
- Registrar e retornar apenas oportunidades válidas; falhas de dados devem virar “erro de fonte” no log e saída reduzida, sem impedir o carregamento do restante.
- Cobrir os cenários com artefatos de teste para evitar regressão.

## Capabilities

### New Capabilities

- `monitor-candles-api`: estabilidade e cobertura de `GET /api/market/candles` para timeframes de operação do Monitor.

### Modified Capabilities

- `opportunity-monitor`: contratos de observabilidade/operabilidade para oportunidade quando parte do conjunto de dados falha.

## Impact

- Backend:
  - `backend/app/api.py` (endpoint `/api/market/candles`, validação de timeframe/route de provider).
  - `backend/app/services/opportunity_service.py` (coleta paralela com timeout por lote e falha por estratégia isolada).
- Testes:
  - `backend/tests/integration/test_market_candles_endpoint.py`
  - `backend/tests/unit/test_opportunity_service_coverage.py`
