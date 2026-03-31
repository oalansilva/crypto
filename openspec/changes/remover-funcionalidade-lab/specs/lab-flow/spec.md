## REMOVED Requirements

### Requirement: Template Draft Não Persistido

#### Scenario: Desenvolvimento de estratégia
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais suportar runs de Lab nem candidatos temporários de template durante esse fluxo

### Requirement: Template Só Persiste Após Aprovação

#### Scenario: Trader aprova estratégia
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais suportar o fluxo de aprovação de estratégias geradas pelo Lab

### Requirement: Template Rejeitado é Descartado

#### Scenario: Trader rejeita estratégia
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais suportar rejeição de estratégias originadas por runs do Lab

### Requirement: Remover Auto-Save de Templates

#### Scenario: Execução de candidato
- **WHEN** a funcionalidade Lab é removida do produto
- **THEN** o sistema não precisa mais suportar execução de candidatos gerados pelo Lab
