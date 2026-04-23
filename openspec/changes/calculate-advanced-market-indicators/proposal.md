## Why

O scoring e os fluxos de análise precisam de sinais técnicos mais ricos do que EMA/SMA/RSI/MACD para capturar volatilidade, momentum, volume e contexto de tendência. Hoje alguns desses cálculos existem apenas dentro de motores de estratégia, mas não como indicadores persistidos, auditáveis e validados no pipeline dedicado de indicadores.

## What Changes

- Calcular indicadores avançados para cada par `symbol`/`timeframe` ativo:
  - Bollinger Bands: banda superior, média e inferior.
  - ATR.
  - Stochastic: linhas `%K` e `%D`.
  - OBV.
  - Ichimoku: Tenkan, Kijun, Senkou Span A, Senkou Span B e Chikou.
- Persistir esses indicadores no armazenamento dedicado de indicadores de mercado, mantendo unicidade por `symbol`, `timeframe` e timestamp.
- Manter recálculo incremental e idempotente, seguindo o mesmo padrão operacional dos indicadores básicos.
- Documentar as fórmulas usadas para cada indicador, incluindo parâmetros padrão e deslocamentos quando aplicável.
- Validar os resultados por indicador com comparação cruzada contra 3 fontes de referência.
- Garantir que o scoring possa consumir os indicadores avançados persistidos sem recalcular em linha.
- Corrigir divergências conhecidas entre cálculos atuais de estratégia e as fórmulas documentadas quando esses cálculos forem reaproveitados.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `market-indicators`: Expande o pipeline dedicado de indicadores para incluir Bollinger, ATR, Stochastic, OBV e Ichimoku, com documentação de fórmulas, persistência, recálculo incremental e validação cruzada.

## Impact

- Backend: serviço de cálculo de indicadores, rotinas de recompute, leitura de OHLCV, consumo pelo scoring e possível reaproveitamento/correção de lógica já existente em estratégias.
- Banco de dados: expansão da tabela `market_indicator` ou definição de armazenamento equivalente para séries avançadas com metadados e integridade.
- Testes: novos fixtures e testes de paridade para TradingView e validação cruzada com TA-Lib/fórmulas independentes onde aplicável.
- Documentação/OpenSpec: fórmulas, parâmetros padrão, fontes de referência e tolerâncias aceitas por indicador.
- Operação: recompute/backfill dos novos campos para ativos e timeframes já armazenados.
