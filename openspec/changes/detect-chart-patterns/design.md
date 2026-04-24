## Context

O projeto já possui um pipeline dedicado em `MarketIndicatorService` que calcula e persiste indicadores por `symbol`/`timeframe`/`ts` na tabela `market_indicator`. Esse pipeline já é incremental, idempotente e usado por consumidores de scoring/monitor para evitar recálculo inline.

Padrões gráficos devem seguir o mesmo caminho: cálculo determinístico no backend, persistência auditável e leitura por consumidores existentes. A feature precisa evitar spam, então os padrões devem ser emitidos como eventos apenas quando há confirmação no candle atual e devem ser deduplicados em uma janela curta.

## Goals / Non-Goals

**Goals:**

- Detectar golden cross, death cross, double top e double bottom com regras custom determinísticas.
- Retornar confiança inteira de 0 a 100 para cada evento.
- Persistir eventos em `market_indicator.chart_patterns` como JSONB nullable.
- Emitir eventos somente no candle de confirmação e deduplicar padrões repetidos em candles próximos.
- Manter o pipeline incremental/idempotente e sem dependência externa nova.

**Non-Goals:**

- Criar uma biblioteca genérica para todos os padrões técnicos.
- Alterar pesos de scoring ou regras de compra/venda.
- Adicionar UI nova para exibir padrões.
- Usar LLM ou serviço externo em runtime.
- Detectar padrões intrabar em candles ainda abertos.

## Decisions

### Decision: Regras custom em vez de dependência externa

A primeira versão usa regras custom em pandas/numpy porque os padrões solicitados são bem delimitados e já temos indicadores calculados no pipeline. Isso evita dependências novas, reduz variação de interpretação entre bibliotecas e mantém determinismo.

Alternativa considerada: biblioteca de pattern recognition. Rejeitada nesta fase porque bibliotecas costumam focar padrões de candle individuais ou retornam sinais sem semântica de confiança/deduplicação alinhada ao produto.

### Decision: Persistir eventos por candle em JSONB

`chart_patterns` será uma lista JSON por linha de `market_indicator`, normalmente vazia ou `NULL`. Cada evento contém `pattern`, `direction`, `confidence`, `ts`, `reference_price`, `source`, `dedupe_key` e `metadata`.

Alternativa considerada: tabela separada de eventos. Rejeitada para esta primeira entrega porque o consumo esperado acompanha a série de indicadores, e JSONB mantém a mudança pequena. Uma tabela dedicada pode ser criada depois se houver workflow próprio para alertas/histórico.

### Decision: Golden/death cross usam SMA 20/50

O pipeline já persiste `sma_20` e `sma_50`; portanto golden cross é o cruzamento de `sma_20` acima de `sma_50`, e death cross é o cruzamento abaixo. O metadado registra `fast_ma=sma_20` e `slow_ma=sma_50`.

Alternativa considerada: SMA 50/200 clássico. Rejeitada nesta entrega porque `sma_200` não existe no armazenamento atual e exigiria ampliar lookback/storage além do escopo pedido.

### Decision: Double top/bottom usam pivôs locais e tolerância percentual

Double top exige dois pivôs altos próximos em preço, separados por distância mínima, com vale intermediário e confirmação por fechamento abaixo do neckline. Double bottom usa a regra espelhada com pivôs baixos e fechamento acima do neckline.

Confiança combina similaridade entre os dois pivôs, profundidade do neckline e força da confirmação. A pontuação é sempre limitada a 0-100.

### Decision: Deduplicação por tipo/direção e janela de barras

Após detectar eventos candidatos, o detector mantém apenas o primeiro evento por `pattern`/`direction` dentro de uma janela padrão de 10 candles. Para double top/bottom, a deduplicação também usa a assinatura dos pivôs para evitar reemitir a mesma estrutura enquanto a confirmação continua válida.

## Risks / Trade-offs

- [Risk] SMA 20/50 pode divergir da interpretação clássica de golden/death cross. -> Mitigation: metadados explícitos e possibilidade futura de adicionar SMA 200.
- [Risk] Double top/bottom são padrões subjetivos. -> Mitigation: regras documentadas, testes determinísticos e confiança calculada por critérios visíveis.
- [Risk] JSONB limita consultas analíticas complexas. -> Mitigation: manter como primeira entrega e migrar para tabela dedicada se alertas/histórico exigirem.
- [Risk] Recompute incremental pode não ter contexto suficiente para padrões longos. -> Mitigation: usar a janela existente de 300 candles, suficiente para as regras iniciais.

## Migration Plan

1. Adicionar `chart_patterns JSONB` em `market_indicator` e schema guard.
2. Implementar detector determinístico em serviço isolado.
3. Integrar cálculo ao `_compute_indicators` e serialização no upsert.
4. Retornar `chart_patterns` em `get_latest`/`get_time_series`.
5. Adicionar testes unitários para detecção, confiança, dedup e persistência.
6. Recompute/backfill operacional preenche padrões para históricos existentes.

Rollback: o campo é nullable e consumidores devem tratar ausência como lista vazia. O código pode parar de preencher `chart_patterns` sem quebrar leituras antigas.
