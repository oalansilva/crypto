## REMOVED Requirements

### Requirement: Supply distribution endpoint is registered
**Reason**: A superfície de produto Distribuição de supply foi descontinuada (#309). O endpoint exclusivo e o serviço associado deixam de fazer parte do contrato suportado.
**Migration**: Remover rota `GET /api/onchain/glassnode/{asset}/supply-distribution`, serviço `onchain_supply_distribution_service` e testes exclusivos. Preservar `glassnode_service` e endpoints onchain ainda ativos (mining-metrics, exchange-flows). Clientes/bookmarks do endpoint antigo devem parar de chamá-lo.
