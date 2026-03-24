## ADDED Requirements

### Requirement: Arbitrage entrypoints MUST be retired from the product surface
The system MUST stop exposing arbitrage spread detection as a supported user-facing capability. Primary navigation, dedicated routes, and HTTP endpoints for arbitrage spreads MUST be absent from the active product surface.

#### Scenario: User navigates through the application
- **WHEN** the user browses the application navigation and available routes
- **THEN** the system MUST NOT present an “Arbitragem” navigation item or dedicated arbitrage page

#### Scenario: Client calls a retired arbitrage endpoint
- **WHEN** a client requests `/api/arbitrage/spreads`
- **THEN** the system MUST return a standard not-found response instead of spread data

## REMOVED Requirements

### Requirement: Detect cross-exchange USDT/USDC spreads
**Reason**: A detecção de arbitragem entre exchanges não faz mais parte da superfície suportada do produto.
**Migration**: Remover chamadas ao fluxo de arbitragem e direcionar usuários para workflows ainda suportados, como Monitor, Lab e Combo.

#### Scenario: Arbitrage spread detection no longer runs
- **WHEN** the application starts or receives arbitrage-related traffic
- **THEN** the system MUST NOT iniciar processamento dedicado para detectar spreads entre exchanges

### Requirement: Provide spread detection API response
**Reason**: O endpoint de arbitragem será aposentado junto com a funcionalidade.
**Migration**: Consumidores existentes devem parar de chamar `/api/arbitrage/spreads`; não há endpoint substituto planejado.

#### Scenario: Arbitrage API contract is no longer available
- **WHEN** an integration tries to request spread results from the retired API
- **THEN** the system MUST NOT retornar o payload histórico de oportunidades de arbitragem

### Requirement: Support configurable threshold filtering
**Reason**: O filtro por threshold deixa de existir porque a API de arbitragem será removida.
**Migration**: Remover parâmetros `threshold`, `exchanges` e `symbols` das integrações que dependiam desse fluxo.

#### Scenario: Threshold parameters are ignored by retirement
- **WHEN** a client attempts to call the retired arbitrage flow with threshold parameters
- **THEN** the system MUST treat the arbitrage flow as unavailable rather than applying filtering

### Requirement: No trade execution in spread detection
**Reason**: A requirement exclusiva de um fluxo removido não precisa permanecer ativa após a aposentadoria da capability.
**Migration**: Nenhuma ação adicional; a remoção do fluxo elimina qualquer comportamento associado.

#### Scenario: No arbitrage detection workflow remains
- **WHEN** the arbitrage capability has been removed
- **THEN** there is no remaining spread-detection workflow that could execute or avoid execution trades
