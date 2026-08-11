## Why

O monitor/scoring precisa reconhecer padrões gráficos recorrentes sem depender de análise manual de candle. Golden cross, death cross e estruturas de double top/bottom são sinais comuns, mas hoje não há saída persistida com confiança e deduplicação para evitar spam.

## What Changes

- Detectar automaticamente padrões gráficos por `symbol`/`timeframe` no pipeline dedicado de indicadores:
  - golden cross;
  - death cross;
  - double top;
  - double bottom.
- Persistir eventos detectados com `pattern`, `direction`, `confidence`, timestamp, preço de referência e metadados da regra.
- Usar regras custom determinísticas nesta primeira versão, sem dependência externa nova.
- Incluir confiança normalizada de 0 a 100 para cada padrão.
- Deduplicar eventos para não emitir o mesmo padrão repetidamente em candles próximos.
- Expor os padrões nas leituras existentes de indicadores para consumidores de scoring/monitor.

## Capabilities

### New Capabilities
- `chart-pattern-detection`: Detecção determinística, persistida e deduplicada de padrões gráficos técnicos com confiança normalizada.

### Modified Capabilities
- `market-indicators`: O pipeline de indicadores passa a persistir e retornar padrões gráficos detectados junto aos vetores técnicos por candle.

## Impact

- Backend: `MarketIndicatorService`, novo helper/serviço de detecção de padrões, leituras de `market_indicator`.
- Banco de dados: novo campo JSONB nullable para eventos de padrões por candle.
- Testes: cobertura unitária das regras, confiança 0-100, deduplicação e serialização/upsert.
- Operação: valores antigos permanecem sem padrões até recompute/backfill de indicadores.
