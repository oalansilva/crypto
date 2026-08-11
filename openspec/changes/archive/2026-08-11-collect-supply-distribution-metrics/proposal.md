## Why

O sistema precisa acompanhar distribuicao de supply por faixa de wallets/entities para separar acumulacao estrutural de varejo, holder e grandes carteiras dos sinais puramente tecnicos de preco.

## What Changes

- Coletar distribuicao de supply via Glassnode por faixas de saldo em entities.
- Expor dashboard operacional por faixa de wallets/entities com latest, baseline da janela, delta absoluto, delta percentual e share de supply.
- Agregar cohorts de `shrimps`, `whales` e `hodlers` para leitura direta.
- Detectar movimentacao de whales como variacao do supply nas faixas `>= 1000 BTC` dentro da janela selecionada.
- Emitir alerta `whale-alert` quando a movimentacao absoluta de whales for maior ou igual a `1000 BTC`.
- Expor rota backend e tela frontend para consulta de `24h`, `7d` e `30d`, reaproveitando cache/rate limit/API key do conector Glassnode.

## Capabilities

### New Capabilities
- `supply-distribution-metrics`: Coleta, agrega e apresenta supply por faixa de wallets/entities, cohorts de shrimps/whales/hodlers e alerta de movimentacao de whales.

### Modified Capabilities
- None.

## Impact

- Backend: novos mappings Glassnode para entity supply bands e LTH supply, novo servico de dominio e nova rota em `onchain_metrics`.
- Frontend: nova pagina de dashboard de supply, item de navegacao e consumo da rota on-chain.
- Glassnode: uso de endpoints de entities/supply com intervalo diario e cache existente.
- Testes: cobertura unit/CQ para mapping, agregacao, alertas, rota e tela com API mockada.
- OpenSpec: nova capability `supply-distribution-metrics` documentando contrato de API, dashboard e semantica do alerta.
- Sem migracao de banco nesta entrega.
