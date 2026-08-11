## Context

O conector Glassnode existente centraliza API key, cache, rate limit, normalizacao de pontos e erros de provider. Distribuicao de supply deve seguir o mesmo padrao das entregas on-chain anteriores: o conector conhece endpoints, o servico de dominio calcula janelas/cohorts/alertas, e a rota apenas adapta payload e erros HTTP.

Os endpoints desta entrega foram conferidos na documentacao oficial da Glassnode:

- Entity supply bands: `/v1/metrics/entities/supply_balance_less_0001`, `/supply_balance_0001_001`, `/supply_balance_001_01`, `/supply_balance_01_1`, `/supply_balance_1_10`, `/supply_balance_10_100`, `/supply_balance_100_1k`, `/supply_balance_1k_10k`, `/supply_balance_10k_100k`, `/supply_balance_more_100k`
- Long-Term Holder Supply: `/v1/metrics/supply/lth_sum`

## Goals / Non-Goals

**Goals:**

- Coletar supply por faixas de saldo de entities para assets suportados pelo conector, com foco operacional inicial em BTC.
- Expor API e dashboard por faixa de wallets/entities nas janelas `24h`, `7d` e `30d`.
- Calcular latest, baseline da janela, delta absoluto, delta percentual e share de cada faixa.
- Agregar `shrimps` como entities com menos de `1 BTC`, `whales` como entities com pelo menos `1000 BTC`, e `hodlers` a partir de LTH supply.
- Emitir `whale-alert` quando a variacao absoluta de supply das faixas whale for maior ou igual a `1000 BTC`.
- Reaproveitar cache, rate limit, API key e erros do conector Glassnode.

**Non-Goals:**

- Criar alerta transacional em tempo real de transferencias grandes.
- Persistir historico ou alertas em banco.
- Enviar notificacoes push, Telegram, email ou WebSocket.
- Adicionar suporte para bases alternativas alem de `entity` nesta entrega.

## Decisions

### Base entity para whales e shrimps

O contrato inicial usa `basis=entity`, porque a Glassnode documenta faixas por entities e isso se aproxima melhor de comportamento de whales do que enderecos crus.

Alternativa considerada: misturar address bands e entity bands. Rejeitada porque criaria leituras inconsistentes entre holders, whales e shrimps.

### Whale movement como delta de supply da cohort

`whale_movement` sera a diferenca entre o latest e o primeiro ponto numerico da janela nas faixas `1k-10k`, `10k-100k` e `>100k`. Direcao:

- `accumulation`: delta positivo
- `distribution`: delta negativo
- `flat`: delta zero ou indisponivel

Alternativa considerada: usar um feed de transferencias whale. Rejeitada nesta entrega porque o criterio pede coleta de supply e o provider configurado entrega serie diaria por faixa; feed transacional exigiria outra fonte/semantica.

### Janelas diarias alinhadas em UTC

As series de supply usadas nesta entrega sao diarias. A consulta ao provider busca um dia extra antes do inicio da janela e calcula o baseline pelo ponto diario correspondente a `latest - window`, evitando que a visao `24h` fique sem delta quando `now` cai apos a meia-noite UTC.

### Threshold do alerta

O alerta `whale-alert` dispara quando `abs(whale_movement.change_abs) >= 1000`. O payload inclui threshold, direcao, delta e janela para que o dashboard explique o sinal.

### Contrato de rota

Nova rota:

`GET /api/onchain/glassnode/{asset}/supply-distribution?basis=entity&window=7d`

Query params:

- `basis`: default/fixo `entity`
- `window`: `24h`, `7d` ou `30d`

Resposta:

- `asset`, `basis`, `window`, `interval`, `since`, `until`, `cached`
- `bands`: faixas com `id`, `label`, `min_btc`, `max_btc`, `latest`, `previous`, `change_abs`, `change_pct`, `share_pct`
- `cohorts`: `shrimps`, `whales`, `hodlers`
- `whale_movement`: delta agregado da cohort whale e status do alerta
- `alerts`: lista de alertas, inicialmente `whale-alert`
- `sources`: metadata por metrica Glassnode

### Dashboard frontend

A tela fica em rota protegida `/supply-distribution`, com controles compactos de janela, cards de cohorts, tabela/barras por faixa e painel de alerta. A UI consome a rota backend e usa estado de loading, erro e vazio sem depender de credenciais Glassnode no navegador.

## Risks / Trade-offs

- [Risk] Algumas metricas Glassnode podem exigir plano pago ou ter suporte limitado por asset. -> Mitigation: manter erros de provider/configuracao explicitos e validar primeiro com testes mockados.
- [Risk] `whale-alert` pode ser confundido com alerta transacional em tempo real. -> Mitigation: nomear no payload como variacao de supply por janela e documentar non-goal.
- [Risk] Buscar muitas faixas aumenta creditos/latencia. -> Mitigation: usar intervalo diario, janelas pequenas e cache existente.
- [Risk] Share de supply depende das faixas retornadas pelo provider. -> Mitigation: calcular share contra a soma das faixas numericas retornadas e preservar sources/points no payload.

## Migration Plan

1. Adicionar mappings de supply/entity bands no conector Glassnode.
2. Implementar servico de dominio para janelas, bandas, cohorts e alertas.
3. Expor rota backend e modelos Pydantic.
4. Adicionar dashboard frontend e navegacao.
5. Cobrir servico, conector, rota e UI com testes.

Rollback: remover rota, servico, dashboard e mappings adicionados. Como nao ha migracao de banco, nao ha rollback de dados.
