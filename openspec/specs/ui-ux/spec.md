# ui-ux Specification

## Purpose
TBD - created by archiving change improve-defaults-and-ui. Update Purpose after archive.
## Requirements
### Requirement: Padrão de Data de Início
O formulário de backtest SHALL iniciar com a data de início ("Start Date") configurada para 1 ano antes da data atual.
Atualmente é 1 mês; a mudança visa facilitar testes de longo prazo.

#### Scenario: Abrir Formulário
- DADO que o usuário abre o formulário Custom Backtest
- QUANDO o formulário é renderizado
- ENTÃO o campo "Start Date" deve mostrar a data de hoje menos 365 dias

### Requirement: Padrão de Timeframe
O formulário de backtest SHALL iniciar com o Timeframe "1d" selecionado por padrão.
Atualmente é '4h'; a mudança reflete a preferência do usuário por gráficos diários.

#### Scenario: Ver Timeframe Padrão
- DADO que o usuário abre o formulário
- ENTÃO o dropdown "Timeframe" deve estar selecionado em "1d"

### Requirement: Estilo de Dropdowns
Todos os elementos de seleção (dropdowns) do formulário SHALL ter contraste adequado para leitura.
O fundo do dropdown expandido MUST ser escuro (compatível com o tema dark/glass) e o texto MUST ser claro.
Elementos `<option>` devem respeitar o tema escuro.

#### Scenario: Expandir Dropdown
- DADO que o usuário clica num dropdown (ex: Timeframe ou Symbol)
- QUANDO as opções são exibidas
- ENTÃO o fundo da lista deve ser escuro
- E o texto das opções deve ser branco ou cinza claro
- E não deve haver fundo branco ofuscante

### Requirement: Pre-Optimization Parameter Review (Sequential)
The system MUST display a configuration screen before starting optimization where the user reviews and can modify ALL optimization ranges for indicator parameters and risk management. System pre-fills with market best practices; user can accept defaults or customize; clear indication of market standard vs custom.

### Requirement: Live Progress Tracking (Sequential)
The system MUST provide a real-time web interface showing current stage, progress within stage (e.g., "Testing 5/13 values"), and stage results as they complete.
