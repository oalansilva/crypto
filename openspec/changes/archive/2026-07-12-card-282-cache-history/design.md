## Context

`analysis_candles` pode ser uma janela resumida enquanto `metrics.trades` cobre todo o backtest. O limite superior prova eventos futuros; o primeiro candle salvo não prova o início real do histórico.

## Goals / Non-Goals

**Goals:** preservar histórico válido, rejeitar saídas futuras e manter regeneração quando trades ainda não existem.

**Non-Goals:** alterar cálculo de trades ou métricas.

## Decisions

- Usar somente `coverage_end` como limite temporal autoritativo na leitura de cache parcial.
- Só escrever `trades` no modelo seguro quando a chave original contiver uma lista.

## Risks / Trade-offs

- [Entrada antiga sem candle correspondente] → preservar porque ausência de candle antigo não prova invalidade; saídas futuras continuam bloqueadas.
