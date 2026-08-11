## Context

O serviço on-chain atual usa DeFiLlama/GitHub para sinais por cadeia. A feature Glassnode tem natureza diferente: métricas de asset (`BTC`, `ETH`) com API key, créditos e rate limit. Por isso o conector fica isolado em um service próprio, evitando acoplamento ao fluxo atual de snapshot/sinal.

## Decisions

### Configuração

O conector lê `Settings`:

- `glassnode_api_key`
- `glassnode_base_url`
- `glassnode_rate_limit_per_minute`
- `glassnode_cache_ttl_seconds`

Sem API key configurada, o conector falha cedo com erro explícito e não tenta chamar rede.

### Endpoints

Ruleset inicial de métricas:

- `mvrv`: `/v1/metrics/market/mvrv`
- `nvt`: `/v1/metrics/indicators/nvt`
- `realized_cap`: `/v1/metrics/market/marketcap_realized_usd`
- `sopr`: `/v1/metrics/indicators/sopr`

Cada chamada usa `a`, `i`, `s`, `u`, `f=json` e autenticação por header `X-Api-Key`, conforme a documentação oficial da Glassnode.

### Cache

Cache em memória keyed por:

- metric
- asset
- interval
- since
- until

TTL padrão: `900` segundos, ou 15 minutos.

### Rate limit

Um limiter assíncrono serializa chamadas e garante espaçamento mínimo entre requests calculado a partir de `glassnode_rate_limit_per_minute`. O cache é checado antes do limiter para não consumir orçamento em hits locais.

### Contrato de rota

`GET /api/onchain/glassnode/{asset}` retorna:

- `asset`
- `interval`
- `cached`
- `metrics`: lista com `metric`, `endpoint`, `points`, `latest`, `fetched_at`, `cached_until`

`asset` aceita apenas `BTC` e `ETH`.
