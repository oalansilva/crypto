## ADDED Requirements

### Requirement: Ver Trades mantém o gráfico visível

No Monitor, ao abrir o modal via **Ver Trades**, o gráfico de candles deve permanecer visível depois que a lista de trades carregar, em desktop e mobile.

#### Scenario: gráfico permanece após load dos trades

- **WHEN** o usuário clica em Ver Trades em uma oportunidade do Monitor
- **AND** o modal carrega candles e, em seguida, a lista de trades
- **THEN** o gráfico (`chart-modal-main-chart`) permanece visível
- **AND** a tabela de trades (`chart-modal-trades`) também permanece visível

#### Scenario: gráfico não colapsa com muitos trades

- **WHEN** a lista de trades ocupa altura significativa no modal
- **THEN** o gráfico mantém altura mínima utilizável (não colapsa para zero)
- **AND** a área de trades usa scroll próprio se necessário

#### Scenario: Abrir Gráfico sem regressão

- **WHEN** o usuário clica em Abrir Gráfico
- **THEN** o modal abre o gráfico sem a tabela de trades
- **AND** o gráfico permanece utilizável como antes desta mudança
