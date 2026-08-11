## Why

O monitor/scoring precisa de níveis técnicos objetivos de suporte e resistência para cada timeframe, sem depender de cálculo manual ou lógica duplicada no frontend. Pivot points clássicos oferecem níveis S1-S3 e R1-R3 determinísticos a partir do candle anterior de cada timeframe.

## What Changes

- Calcular pivot point clássico por `symbol`/`timeframe` usando OHLC do candle anterior.
- Persistir por candle os níveis:
  - `pivot_point`
  - `support_1`, `support_2`, `support_3`
  - `resistance_1`, `resistance_2`, `resistance_3`
- Atualizar os níveis sempre que o pipeline de indicadores processar candles do timeframe correspondente.
- Manter warmup nulo para o primeiro candle sem candle anterior.
- Expor os níveis nas leituras existentes de indicadores para scoring/monitor.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `market-indicators`: Expande o pipeline dedicado de indicadores para calcular, persistir e retornar níveis dinâmicos de suporte/resistência por pivot points em cada timeframe.

## Impact

- Backend: `MarketIndicatorService` passa a calcular e persistir níveis S1-S3/R1-R3.
- Banco de dados: novos campos numéricos nullable em `market_indicator`.
- API: leituras de indicadores retornam os níveis de suporte/resistência junto aos demais indicadores.
- Testes: cobertura unitária para fórmula clássica, warmup nulo, upsert/read shape e atualização por timeframe.
