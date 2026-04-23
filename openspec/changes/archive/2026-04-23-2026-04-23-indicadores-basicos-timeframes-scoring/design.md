# Design

## Context

A camada de scoring precisa de indicadores técnicos com baixa latência e reprodutibilidade. A ausência de uma tabela dedicada com atualização incremental cria risco de inconsistência e custo alto de recálculo.

## Goals

- Criar cálculo determinístico de EMA, SMA, RSI e MACD por timeframe.
- Atualizar indicadores de forma incremental conforme novos candles chegam.
- Persistir os valores em tabela dedicada, com metadados de origem e execução.
- Garantir validação numérica contra TradingView em CI/local para evitar regressão.

## Non-Goals

- Mudar a lógica de geração de candles/ohlcv.
- Alterar estratégia de score sem contrato técnico explícito.
- Calcular indicadores exóticos fora do escopo base.

## Decisions

1. **Biblioteca padrão: TA-Lib**
- Será usada por padrão para geração de EMA, SMA, RSI e MACD.
- A implementação deve importar apenas `talib` como motor de runtime para reduzir overhead e padronizar desempenho.
- Parâmetros-padrão: `EMA 9/21`, `SMA 20/50`, `RSI 14`, `MACD 12/26/9`.
- Não haverá fallback de biblioteca para este escopo. A execução operacional deve depender apenas de TA-Lib.

2. **Timeframes alvo explícitos**
- `1m, 5m, 15m, 1h, 4h, 1d` (configuráveis).

3. **Janela de fechamento da vela e timezone**
- Time base em UTC.
- Indicadores calculados no fechamento de vela (`close`) com candle já finalizado.

4. **Persistência dedicada**
- Tabela `market_indicator` com PK única em `(symbol, timeframe, ts)`.
- Armazenar apenas valores úteis e metadados (`source_window`, `row_count`, `is_recomputed`, `updated_at`).

5. **Recompute incremental**
- Para cada novo candle, recalcular indicadores usando janela mínima de segurança:
  - `max_lookback = 300` candles (ou maior do parâmetro de maior janela configurada).
- On correction ou reprocesso forçado, reprocessar janela recente e atualizar registros idempotentemente.

6. **Validação TradingView**
- Pipeline de testes com fixtures de referência (export CSV de TradingView).
- Comparar `close` alinhado e validar com tolerância numérica (`atol=1e-6`, `rtol=1e-5`) para pontos válidos.

## Risks / Trade-offs

- Pequenas diferenças de arredondamento entre provedores e métodos (`adjust`, `na_mode`) podem gerar diffs pontuais; mitigamos com tolerância e janela de aceitação definida por indicador.
- Timeframes menores (`1m/5m`) podem gerar volume de recálculo maior; mitigamos com recálculo incremental e checkpoints.

## Open Questions

- Existe fonte de referência TradingView interna ou precisamos manter fixtures manuais versionados no repo?
