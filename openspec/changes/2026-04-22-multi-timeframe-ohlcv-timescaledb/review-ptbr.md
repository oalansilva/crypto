# Revisão PT-BR — multi-timeframe-ohlcv-timescaledb

Objetivo desta change:
- Persistir candles OHLCV no banco em `TimescaleDB` (hypertable), cobrindo os timeframes `1m`, `5m`, `1h`, `4h`, `1d`.
- Garantir retenção mínima de 2 anos e compressão automática após 30 dias.
- Entregar leitura mais rápida para `/api/market/candles` com alvo de resposta `< 500ms` em janelas normais.

Escopo aprovado para implementação:
- Modelagem de banco + policies de retenção/compressão.
- Ingestão contínua e idempotente por timeframe/símbolo.
- Ajuste de API/serviço de consulta para priorizar Timescale e evitar recálculo excessivo.

Pontos de decisão:
- Vamos manter provider fallback só como contingência.
- Queries terão janela/limite explícitos para preservar latência.
- Métricas mínimas: lag de ingestão, duplicados ignorados, latência de consulta.

Resumo rápido para o Alan:
- Está pronta a trilha de OpenSpec para iniciar implementação.
- Change id sugerido: `2026-04-22-multi-timeframe-ohlcv-timescaledb`.
- Artifacts: `proposal`, `specs/ohlcv-storage/spec`, `tasks`, `design`, este review.
