## ADDED Requirements

### Requirement: Batch backtest from Configure Backtest screen
The system SHALL allow the user to trigger a **batch backtest** from the `Configure Backtest` screen, using the current configuration to run backtests for multiple symbols automatically and save resulting strategies into favorites.

#### Scenario: Run batch backtest for user-selected symbols
- **GIVEN** the user has preenchido a configuração na tela `Configure Backtest` (template, parâmetros/ranges, timeframe, flags como `Deep Backtest`)
- **AND** a lista de símbolos disponíveis está carregada no seletor de `Symbol`
- **AND** the user selecionou o escopo do batch (único símbolo atual, lista multi‑selecionada x,y,z, ou todos os símbolos disponíveis/filtrados)
- **WHEN** the user clicks the **“Run Batch”** (or equivalent) action on this screen
- **THEN** the system MUST iterar exatamente sobre a lista de símbolos escolhida
- **AND** para cada símbolo MUST disparar um backtest/otimização com a mesma configuração de parâmetros e timeframe da tela
- **AND** MUST executar todos os símbolos do lote sem exigir interação manual para cada um.

#### Scenario: Save best result of each symbol as new favorite with batch note and Tier 3
- **GIVEN** um batch backtest foi disparado a partir da tela `Configure Backtest`
- **AND** o backtest para um determinado símbolo completa com sucesso
- **WHEN** o sistema determina o melhor resultado para aquele símbolo (seguindo a lógica já existente de seleção de “best result”)
- **THEN** the system MUST criar **um novo** registro em `favorite_strategies` contendo:
  - o símbolo, timeframe e template usados
  - os parâmetros finalistas da estratégia
  - as principais métricas de performance associadas
- **AND** MUST definir o campo `notes` desse favorito com um comentário específico indicando que foi **gerado em lote** (por exemplo `\"gerado em lote\"` + timestamp ou id do batch)
- **AND** MUST definir `tier = 3` para todas as estratégias geradas por esse batch.

#### Scenario: Batch feedback and errors per symbol
- **GIVEN** um batch backtest foi iniciado
- **WHEN** pelo menos um símbolo falha (por exemplo, sem dados, erro de exchange, erro de backtest)
- **THEN** the system MUST registrar a falha em logs com o símbolo e motivo
- **AND** MUST continuar processando os demais símbolos do lote
- **AND** the frontend MUST apresentar ao usuário um resumo ao final contendo:
  - quantidade de símbolos processados com sucesso
  - quantidade de símbolos que falharam
  - indicação de onde revisar os favoritos criados (ex.: link para `Strategy Favorites` ou `Opportunity Board`).

