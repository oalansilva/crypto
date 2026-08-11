## Why

O sistema precisa acompanhar métricas estruturais de mineração para detectar pressão operacional na rede Bitcoin, separando sinais de infraestrutura de sinais puramente técnicos de preço.

## What Changes

- Coletar hash rate, difficulty e métricas de mineração a partir do conector Glassnode existente.
- Expor médias móveis de 7d e 30d por métrica.
- Rastrear ATH por métrica dentro da série retornada.
- Emitir alerta quando o valor atual cair mais de 10% contra a média móvel de 7d.
- Expor rota backend para consulta agregada por asset, mantendo cache/rate limit/API key do conector atual.

## Capabilities

### New Capabilities
- `mining-network-metrics`: Coleta e agrega métricas de mineração com médias móveis, ATH e alerta de queda brusca.

### Modified Capabilities
- None.

## Impact

- Backend: novo serviço de domínio para agregação de métricas de mineração e nova rota em `onchain_metrics`.
- Glassnode: novos mappings de endpoint para hash rate, difficulty e métrica de mineração.
- Testes: cobertura unitária para médias móveis, ATH, alerta >10%, payload vazio e erro de provider/configuração.
- OpenSpec: nova capability `mining-network-metrics` documentando contrato de API e regras de alerta.
- Sem migração de banco nesta entrega.
