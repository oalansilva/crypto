## ADDED Requirements

### Requirement: Button component padronizado
O sistema DEVE fornecer componente Button com variantes consistentes.

#### Scenario: Button primary
- **WHEN** Button variant="primary" é usado
- **THEN** renderiza com cor de acento e shadow

#### Scenario: Button secondary
- **WHEN** Button variant="secondary" é usado
- **THEN** renderiza com fundo neutro e borda

#### Scenario: Button ghost
- **WHEN** Button variant="ghost" é usado
- **THEN** renderiza sem fundo, apenas texto

#### Scenario: Button sizes
- **WHEN** props sm, md, lg são usados
- **THEN** altura do botão é 36px, 42px, 50px respectivamente

### Requirement: Input component padronizado
O sistema DEVE fornecer componente Input com estilos consistentes.

#### Scenario: Input padrão
- **WHEN** Input é renderizado
- **THEN** tem altura de 48px, borda e focus state com accent

#### Scenario: Input com erro
- **WHEN** Input tem prop error
- **THEN** borda fica em cor danger e mostra mensagem

### Requirement: Card component padronizado
O sistema DEVE fornecer componente Card com estilos consistentes.

#### Scenario: Card padrão
- **WHEN** Card é renderizado
- **THEN** tem background, borda sutil, border-radius e shadow

### Requirement: Badge component
O sistema DEVE fornecer componente Badge para labels e status.

#### Scenario: Badge variants
- **WHEN** Badge variants (primary, success, warning, danger) são usados
- **THEN** cores correspondentes são aplicadas

### Requirement: Sidebar/Nav component
O sistema DEVE fornecer componente de navegação lateral.

#### Scenario: Sidebar desktop
- **WHEN** viewport >= 1024px
- **THEN** sidebar fixa à esquerda com ícones e labels

#### Scenario: Sidebar mobile
- **WHEN** viewport < 1024px
- **THEN** pode ser colapsada ou transformada em bottom nav

### Requirement: Modal/Dialog component
O sistema DEVE fornecer componente Modal com overlay e centralização.

#### Scenario: Modal abre
- **WHEN** Modal é mounted com isOpen=true
- **THEN** overlay escurece fundo e modal aparece centralizado

### Requirement: Dropdown component
O sistema DEVE fornecer componente DropdownMenu.

#### Scenario: Dropdown abre
- **WHEN** Dropdown é acionado
- **THEN** menu aparece com opções estilizadas
