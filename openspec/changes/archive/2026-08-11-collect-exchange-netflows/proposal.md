## Why

O sistema já consegue consultar métricas on-chain da Glassnode, mas ainda não entrega exchange flows em uma forma pronta para decisão: inflow, outflow e netflow precisam ser agregados por exchange e também em total para janelas operacionais padronizadas.

## What Changes

- Coletar exchange inflow, outflow e netflow via Glassnode.
- Agregar valores por exchange quando o payload do provider vier quebrado por exchange.
- Agregar total da janela para inflow, outflow e netflow.
- Suportar janelas `24h`, `7d` e `30d`.
- Expor endpoint backend para consulta dos flows por asset e janela.

## Capabilities

### New Capabilities
- `exchange-netflows`: Normaliza e agrega exchange flows por exchange e total.

### Modified Capabilities
- `glassnode-onchain-connector`: Expande o conector Glassnode para coletar flows de exchanges.

## Impact

- Backend: extensão do `GlassnodeService` e da rota `/api/onchain`.
- Testes: cobertura unitária para janelas, inflow/outflow/netflow, agregação por exchange, fallback total e rota.
- Sem migração de banco; entrega cache-only usando o conector Glassnode existente.
