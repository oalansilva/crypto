## ADDED Requirements

### Requirement: Dark theme como padrão
O sistema DEVE usar o tema dark como padrão ao carregar a aplicação.

#### Scenario: Tema dark aplicado por padrão
- **WHEN** a aplicação é iniciada
- **THEN** as cores de fundo e texto usam os valores dark (--bg-primary: #09090b, --text-primary: #fafafa)

### Requirement: Paleta de cores dark com contraste WCAG AA
O sistema DEVE garantir que a paleta de cores dark tenha contrast ratio mínimo de 4.5:1 para texto normal.

#### Scenario: Contraste verificado
- **WHEN** text-primary (#fafafa) é usado em bg-primary (#09090b)
- **THEN** o ratio é maior que 4.5:1

### Requirement: Cores de acento para dark theme
O sistema DEVE definir cores de acento que funcionam bem em fundo escuro.

#### Scenario: Accent colors disponíveis
- **WHEN** cores de acento são necessárias
- **THEN** --accent-primary (emerald), --accent-cyan, --accent-secondary (violet) estão definidas

### Requirement: Estados de componentes com bom contraste
O sistema DEVE garantir que estados como hover, focus, active mantenham contraste adequado.

#### Scenario: Hover com contraste
- **WHEN** usuário faz hover em botão
- **THEN** a cor de fundo muda mas mantém contraste mínimo 3:1

### Requirement: Suporte a theme switching (futuro)
O sistema DEVE estar preparado para alternância de tema via CSS variables.

#### Scenario: Theme switching preparado
- **WHEN** classes de tema são aplicadas ao root
- **THEN** as variáveis CSS se adaptam automaticamente
