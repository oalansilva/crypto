## Context

O projeto já possui o pipeline `MarketIndicatorService`, que lê `market_ohlcv`, calcula indicadores por `symbol`/`timeframe` e persiste em `market_indicator` com unicidade `(symbol, timeframe, ts)`. Essa trilha já é incremental, idempotente e consumida por scoring/monitor.

Suporte/resistência por pivot deve seguir a mesma trilha para evitar cálculo no frontend ou em consumidores de scoring. Como pivot clássico depende do OHLC do candle anterior do mesmo timeframe, os níveis são naturalmente atualizados a cada candle/timeframe processado.

## Goals / Non-Goals

**Goals:**

- Calcular pivot clássico, S1-S3 e R1-R3 por candle processado.
- Usar exclusivamente OHLC do candle anterior do mesmo `symbol`/`timeframe`.
- Persistir níveis como colunas numéricas nullable em `market_indicator`.
- Manter primeiro candle como nulo por falta de candle anterior.
- Incluir níveis nas leituras `get_latest` e `get_time_series`.

**Non-Goals:**

- Implementar variações Fibonacci, Camarilla, Woodie ou DeMark.
- Criar UI nova para desenhar níveis no gráfico.
- Alterar scoring ou lógica de entrada/saída.
- Criar alertas quando preço toca suporte/resistência.

## Decisions

### Decision: Usar pivot clássico

Fórmulas:

- `P = (Hprev + Lprev + Cprev) / 3`
- `R1 = (2 * P) - Lprev`
- `S1 = (2 * P) - Hprev`
- `R2 = P + (Hprev - Lprev)`
- `S2 = P - (Hprev - Lprev)`
- `R3 = Hprev + 2 * (P - Lprev)`
- `S3 = Lprev - 2 * (Hprev - P)`

Alternativa considerada: pivot Fibonacci. Rejeitada porque o DoD pede algoritmo de pivot points e níveis S1-S3/R1-R3 sem especificar variante; clássico é o padrão mais simples e auditável.

### Decision: Persistir em colunas explícitas

Os níveis são estáveis e usados em consultas/scoring, então colunas numéricas explícitas são melhores que JSONB para legibilidade, filtros e validação.

### Decision: Integrar ao pipeline de indicadores

O cálculo entra em `_compute_indicators` junto aos demais valores derivados de OHLCV. Isso preserva incrementalidade, idempotência e atualização por timeframe sem criar job novo.

## Risks / Trade-offs

- [Risk] O primeiro candle de cada janela incremental pode perder contexto do candle anterior se a janela começar depois do histórico real. -> Mitigation: a janela incremental já recua `LOOKBACK_BARS`, dando contexto suficiente para recalcular o trecho recente; primeiro registro da janela pode ficar nulo, mas registros seguintes usam o candle anterior da janela.
- [Risk] Usuários podem esperar variações diferentes de pivot. -> Mitigation: documentar explicitamente que esta entrega usa pivot clássico.
- [Risk] Adicionar colunas aumenta largura da tabela. -> Mitigation: o conjunto é fixo e pequeno.

## Migration Plan

1. Adicionar colunas nullable em `market_indicator` via Alembic e schema guard.
2. Calcular pivot/S/R em `_compute_indicators` com `shift(1)`.
3. Incluir colunas no select e upsert.
4. Adicionar testes de fórmula, warmup e serialização.
5. Recompute/backfill operacional para preencher históricos existentes.

Rollback: as colunas são nullable; rollback pode removê-las via Alembic sem afetar indicadores existentes.
