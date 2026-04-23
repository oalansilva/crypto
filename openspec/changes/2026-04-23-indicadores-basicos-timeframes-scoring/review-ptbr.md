# Review PT-BR — Indicadores básicos por timeframe para scoring

## Resumo

- Projeto: `crypto`
- Change ID: `2026-04-23-indicadores-basicos-timeframes-scoring`
- Objetivo: padronizar e persistir cálculos de EMA, SMA, RSI e MACD para uso de scoring em todos os timeframes.

## O que foi definido

- Escolhido `TA-Lib` como motor técnico exclusivo.
- Timeframes-alvo explícitos: `1m,5m,15m,1h,4h,1d`.
- Dados em UTC, baseados em `close` de vela finalizada.
- Indicadores devem ser persistidos em tabela dedicada (`market_indicator`) com unicidade por `(symbol, timeframe, ts)`.
- Validação por fixtures de TradingView com tolerância numérica.

## Decisão necessária

- Definir ainda:
  - janelas/tuning finais (se manter os valores padrão definidos nesta change);
  - política de retenção/expurgo de `market_indicator` por período.
- Resultado atual:
  - O fluxo desta change foi implementado com `TA-Lib` apenas para o pipeline de `market_indicator` e scoring.

## Tradeoffs

- Recalcular incremental reduz custo operacional, mas exige controle rigoroso de checkpoint e correção retroativa.
- TradingView fixtures elevam confiança de precisão, porém geram custo de manutenção de dados de referência.

## Próximo passo

- Próximo owner recomendado: `DEV`
- Próxima ação: completar validação contra fixtures TradingView e fechar `openspec validate`.

## Decisão já tomada

- A escolha é **TA-Lib exclusivo**, sem mecanismo de fallback.
