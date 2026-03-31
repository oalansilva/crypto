## REMOVED Requirements

### Requirement: Consistent Run State

#### Scenario: Upstream not yet executed
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais manter `status` e `phase` específicos de run do Lab

#### Scenario: Execution started
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais refletir estados de execução de runs do Lab

### Requirement: Managed Execution Worker

#### Scenario: Worker-managed run
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais enfileirar nem executar runs do Lab em worker dedicado

### Requirement: Retry With Reasons Fallback

#### Scenario: Required fixes present
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais suportar retries de estratégias geradas pelo Lab

#### Scenario: Required fixes missing
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais suportar fallback de `required_fixes` ou `reasons` para retries do Lab

### Requirement: Output Schema Validation

#### Scenario: Valid JSON output
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais validar saídas estruturadas de Trader/Dev para runs do Lab

#### Scenario: Invalid JSON output
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais aplicar fallback de validação para saídas do Lab

### Requirement: Run Timeouts

#### Scenario: Node timeout
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais controlar timeouts por nó em runs do Lab

#### Scenario: Total timeout
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais controlar timeout total de runs do Lab
