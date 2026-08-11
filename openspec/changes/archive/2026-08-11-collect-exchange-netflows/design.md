## Context

O conector Glassnode atual já centraliza API key, cache e rate limit. A nova feature deve reaproveitar esse conector, evitando outro cliente HTTP e preservando o uso de `X-Api-Key`.

## Decisions

### Endpoints

- `inflow`: `/v1/metrics/transactions/transfers_volume_to_exchanges_sum`
- `outflow`: `/v1/metrics/transactions/transfers_volume_from_exchanges_sum`
- `netflow`: `/v1/metrics/transactions/transfers_volume_exchanges_net`

### Windows

Janelas suportadas:

- `24h`: 1 dia
- `7d`: 7 dias
- `30d`: 30 dias

O serviço calcula `since`/`until` em Unix seconds a partir do relógio injetável do service. A chamada usa `i=24h` para manter granularidade diária e reduzir custo de API.

### Agregação

Cada endpoint retorna uma série temporal Glassnode. O valor `v` pode ser:

- número: agregado total do provider;
- objeto: quebra por exchange;
- array: preservado pelo parser, mas ignorado para agregação numérica se não houver pares nomeados.

A regra:

- se `v` é objeto, somar cada chave como exchange ao longo da janela;
- se `v` é número, somar no bucket `total`;
- o total de cada métrica é a soma de todos os buckets de exchange quando existem exchanges, ou o bucket `total` quando o provider retorna escalar.

Para cada exchange:

- `inflow` vem do endpoint de entradas;
- `outflow` vem do endpoint de saídas;
- `netflow` usa endpoint de netflow quando disponível para a exchange;
- se netflow por exchange não existir, é calculado como `inflow - outflow`.

### API

`GET /api/onchain/glassnode/{asset}/exchange-flows?window=24h|7d|30d`

Retorna:

- `asset`
- `window`
- `interval`
- `since`
- `until`
- `cached`
- `total`
- `exchanges`
- `sources`
