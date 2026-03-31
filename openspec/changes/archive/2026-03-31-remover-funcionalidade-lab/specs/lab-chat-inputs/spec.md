## REMOVED Requirements

### Requirement: Remover inputs de Symbol/Timeframe/Template base do /lab

#### Scenario: Usuário acessa a página /lab
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** a página `/lab` deixa de existir
- **AND** o sistema não precisa mais manter regras de UI específicas para inputs do Lab

### Requirement: Preflight determinístico de inputs obrigatórios antes de iniciar run

#### Scenario: Payload sem symbol/timeframe
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o backend não precisa mais aceitar nem validar payloads de criação de run do Lab

#### Scenario: Payload completo
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o backend não precisa mais iniciar runs do Lab com `symbol` e `timeframe`

### Requirement: UI deve lidar com needs_user_input

#### Scenario: Backend pede input
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o frontend não precisa mais exibir `needs_user_input` nem perguntas de continuação relacionadas ao Lab
