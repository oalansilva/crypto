## Context

O conector Glassnode existente já centraliza API key, cache, normalização básica de pontos, rate limit e erros de provider. Métricas de mineração entram na mesma família on-chain, mas as regras de média móvel, ATH e alerta são lógica de domínio e não devem ficar no cliente HTTP.

Os endpoints de mineração usados nesta entrega foram conferidos na documentação da Glassnode:

- `difficulty`: `/v1/metrics/mining/difficulty_latest`
- `hash_rate`: `/v1/metrics/mining/hash_rate_mean`
- `miner_revenue_total`: `/v1/metrics/mining/revenue_sum`

## Goals / Non-Goals

**Goals:**

- Coletar hash rate, difficulty e receita total de mineração para assets suportados pelo conector.
- Calcular média móvel trailing de 7 e 30 pontos diários por métrica.
- Rastrear ATH por métrica dentro da série retornada pela consulta.
- Emitir alerta quando o valor mais recente ficar mais de 10% abaixo da média móvel de 7d.
- Reaproveitar cache, rate limit, API key e tratamento de erros do conector Glassnode.

**Non-Goals:**

- Persistir métricas de mineração em banco.
- Criar UI para essas métricas.
- Criar alertas assíncronos/notificações push.
- Adicionar métricas por pool/miner individual.

## Decisions

### Separar conector e agregação

`backend/app/services/glassnode_service.py` recebe apenas o mapping dos novos endpoints. A agregação fica em `backend/app/services/onchain_mining_metric_service.py`, seguindo o padrão já aplicado para exchange flows.

Alternativa considerada: adicionar cálculo direto em `GlassnodeService.fetch_metrics`. Rejeitada porque misturaria regra de negócio com fetch/cache/rate-limit.

### Contrato de rota

Nova rota:

`GET /api/onchain/glassnode/{asset}/mining-metrics`

Query params:

- `interval`: fixed/default `24h`
- `since`: Unix timestamp opcional
- `until`: Unix timestamp opcional

Sem `since`, o provider pode retornar o histórico disponível; nesse caso o ATH é calculado sobre a série retornada. Com `since`, o ATH fica escopado à janela solicitada.

Resposta:

- `asset`
- `interval`
- `since`
- `until`
- `cached`
- `metrics`: lista com `metric`, `endpoint`, `points`, `latest`, `ath`, `alerts`, `fetched_at`, `cached_until`, `cached`

Cada ponto numérico da série inclui:

- `t`
- `v`
- `ma_7d`
- `ma_30d`
- `distance_from_ath_pct`

### Regras numéricas

Valores não numéricos, ausentes, infinitos ou NaN são ignorados no cálculo de médias e ATH. Eles podem permanecer na lista de pontos sem campos derivados.

As médias móveis são trailing sobre pontos diários (`interval=24h`) e exigem janela completa:

- `ma_7d`: só aparece quando há pelo menos 7 valores numéricos até o ponto.
- `ma_30d`: só aparece quando há pelo menos 30 valores numéricos até o ponto.

O alerta `sharp_drop` é emitido apenas quando `latest.v` e `latest.ma_7d` existem e:

`latest.v < latest.ma_7d * 0.9`

### Métricas iniciais

O set inicial fica pequeno para controlar custo de API:

- `hash_rate`
- `difficulty`
- `miner_revenue_total`

Novas métricas de mineração podem ser adicionadas depois apenas pelo mapping do conector e testes de contrato.

## Risks / Trade-offs

- [Risk] Consultas sem `since` podem retornar séries longas e consumir mais créditos/latência. -> Mitigation: manter cache existente e aceitar `since`/`until` para consultas operacionais menores.
- [Risk] ATH sem persistência depende da série retornada pelo provider. -> Mitigation: declarar escopo no contrato e preservar `since`/`until` no payload.
- [Risk] Algumas métricas Glassnode podem retornar payload não escalar. -> Mitigation: derivar MA/ATH/alerta apenas de valores numéricos finitos e preservar pontos brutos quando não forem numéricos.

## Migration Plan

1. Adicionar mappings de métricas de mineração no conector Glassnode.
2. Implementar serviço de domínio para enriquecer séries com MA/ATH/alertas.
3. Expor rota backend e modelos Pydantic.
4. Cobrir agregação e rota com testes unitários.

Rollback: remover a nova rota e o serviço de domínio. Como não há migração de banco, o rollback não exige alteração de dados.
