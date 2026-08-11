## Why

O sistema precisa enriquecer o engine on-chain com métricas de ciclo e valuation vindas da Glassnode. MVRV, NVT, realized cap e SOPR são fontes externas pagas/rate-limited, então o conector precisa centralizar autenticação, cache e controle de chamadas para evitar consumo excessivo de créditos.

## What Changes

- Adicionar conector backend para Glassnode API.
- Coletar MVRV, NVT, realized cap e SOPR para BTC e ETH.
- Tornar API key, base URL, rate limit e TTL de cache configuráveis.
- Aplicar cache em memória de 15 minutos por asset/métrica/janela.
- Respeitar rate limit antes de chamadas externas e expor erro claro em HTTP 429.
- Expor rota backend para consulta das métricas agregadas por asset.

## Capabilities

### New Capabilities
- `glassnode-onchain-connector`: Coleta métricas Glassnode versionadas por endpoint para BTC e ETH.

### Modified Capabilities
- None.

## Impact

- Backend: novo service `glassnode_service` e rota `onchain_metrics`.
- Configuração: novas opções `GLASSNODE_API_KEY`, `GLASSNODE_BASE_URL`, `GLASSNODE_RATE_LIMIT_PER_MINUTE`, `GLASSNODE_CACHE_TTL_SECONDS`.
- Testes: cobertura unitária para API key, cache 15min, rate limit, 429 e BTC/ETH.
- Sem migração de banco nesta entrega.
