## Why

O scoring atual depende de features técnicas consistentes e atualizadas. Hoje os indicadores básicos não estão padronizados por timeframe em uma trilha única persistida, dificultando confiança, rastreabilidade e comparação entre runs.

## What Changes

- Calcular EMA, SMA, RSI e MACD para todos os timeframes de operação existentes.
- Persistir os resultados em uma tabela dedicada de indicadores.
- Implementar recálculo incremental para evitar reprocessamento de histórico completo a cada candle.
- Migrar o motor técnico para `TA-Lib` como padrão exclusivo de cálculo (EMA, SMA, RSI, MACD) no fluxo desta change.
- Adicionar validação contra valores de referência do TradingView.

## New / Modified Capabilities

### New

- `market-indicator-pipeline`: serviço backend para atualizar indicadores técnicos por `(symbol, timeframe)`.
- `technical-indicator-engine`: camada de cálculo técnico usando exclusivamente `TA-Lib`.
- `market_indicator` table: persistência incremental de features técnicas no banco.
- `indicator-reconciliation` job: validação periódica contra dataset de referência.
- `market-indicator-consumption`: consumo de indicadores persistidos em scoring com recálculo mínimo residual.

### Modified

- Pontos de scoring existentes que consumirão indicadores do novo `market_indicator` em vez de calcular inline.
- `ComboStrategy` no caminho de scoring não depende mais de `pandas-ta` para EMA/SMA/RSI/MACD.

## Out of Scope

- Estratégias novas de trading.
- Mudança de provider de preços.
- Reprojeto da estratégia de otimização/engine de score.
