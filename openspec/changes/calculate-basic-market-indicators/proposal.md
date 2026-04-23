## Why

O scoring precisa de indicadores técnicos básicos consistentes, auditáveis e disponíveis para todos os timeframes suportados sem recalcular valores em linha a cada uso. Formalizar este fluxo reduz divergência entre backtest, monitoramento e scoring, e cria uma base confiável para evoluções futuras de indicadores.

## What Changes

- Calcular EMA, SMA, RSI e MACD para cada par `symbol`/`timeframe` ativo a partir dos candles OHLCV fechados.
- Usar uma engine técnica padronizada para runtime, com preferência por TA-Lib quando disponível no ambiente.
- Persistir os vetores de indicadores em uma tabela dedicada com chave única por `symbol`, `timeframe` e timestamp.
- Suportar recálculo incremental/idempotente, evitando recomputar a série inteira em rotinas regulares.
- Expor ou manter um fluxo operacional de recompute para backfill, correção e atualização manual.
- Validar os cálculos com testes automatizados contra valores de referência exportados da TradingView.
- Garantir que o scoring leia os indicadores persistidos, sem recálculo inline.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `market-indicators`: Reforça os requisitos para cálculo, persistência, recálculo incremental, validação TradingView e consumo de EMA/SMA/RSI/MACD pelo scoring.

## Impact

- Backend: serviço de cálculo de indicadores, jobs/admin endpoints de recompute, leitura de candles OHLCV e camada de scoring.
- Banco de dados: tabela dedicada `market_indicator`, campos técnicos, metadados e constraint de unicidade.
- Testes: fixtures TradingView e testes de paridade por indicador/timeframe com tolerância explícita.
- Dependências: TA-Lib ou biblioteca técnica equivalente aprovada para cálculo determinístico.
- Operação: recompute/backfill de indicadores para ativos e timeframes já armazenados.
