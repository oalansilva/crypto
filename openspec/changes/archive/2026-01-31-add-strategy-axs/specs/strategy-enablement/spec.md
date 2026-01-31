## ADDED Requirements
### Requirement: Habilitar Estratégia ESTRATEGIAAXS
O formulário Custom Backtest SHALL permitir selecionar a estratégia "ESTRATEGIAAXS".

#### Scenario: Selecionar ESTRATEGIAAXS
- DADO que o usuário está no formulário Custom Backtest
- QUANDO o usuário clica no botão "ESTRATEGIAAXS"
- ENTÃO a estratégia é selecionada
- E campos de parâmetros específicos aparecem

### Requirement: Carregamento Dinâmico de Parâmetros
O frontend DEVE (MUST) renderizar os campos de parâmetros dinamicamente com base nos metadados da estratégia selecionada recebidos do backend, sem hardcoding de campos no frontend.
Ao selecionar "ESTRATEGIAAXS", os inputs para os 3 parâmetros específicos DEVEM (MUST) aparecer automaticamente.

#### Scenario: Troca de Estratégia
- DADO que o usuário está em uma tela de configuração
- QUANDO o usuário troca a estratégia para "ESTRATEGIAAXS"
- ENTÃO os campos anteriores somem
- E os campos "Media Curta", "Media Longa", "Media Intermediaria" são renderizados dinamicamente

### Requirement: Configuração de Parâmetros ESTRATEGIAAXS
O backend DEVE (MUST) expor metadados definindo os 3 parâmetros para ESTRATEGIAAXS.
Os campos no frontend DEVEM (MUST) refletir esses metadados.
Os valores padrão MUST ser: Media Curta (EMA)=6, Media Longa (SMA)=38, Media Intermediaria (SMA)=21.

#### Scenario: Configurar Parâmetros AXS
- DADO que ESTRATEGIAAXS está selecionada
- QUANDO o usuário visualiza o formulário
- ENTÃO campos "Media Curta", "Media Longa", "Media Intermediaria" são exibidos
- E os valores padrão são 6, 38, 21 respectivamente

### Requirement: Integração ESTRATEGIAAXS com Recursos Comuns
A estratégia ESTRATEGIAAXS DEVE (MUST) suportar os recursos padrão de Stop Loss, Take Profit e Otimização de Parâmetros.
A interface DEVE permitir a configuração de 'Stop Loss' e 'Take Profit' ao selecionar esta estratégia.
- ESTRATEGIAAXS DEVE estar disponível para seleção e configuração na página `/optimize/parameters`.
- ESTRATEGIAAXS DEVE estar disponível para seleção e configuração na página `/optimize/risk`.
Os parâmetros **Media Curta** (EMA), **Media Longa** (SMA) e **Media Intermediaria** (SMA) DEVEM estar disponíveis para configuração nessas interfaces e para seleção de intervalos no modo de otimização ("variações") com os defaults 6, 38 e 21 respectivamente.

#### Scenario: Otimização de Parâmetros AXS
- DADO que o usuário está na página `/optimize/parameters`
- QUANDO ESTRATEGIAAXS é selecionada
- ENTÃO é possível definir ranges (início, fim, passo) para "Media Curta", "Media Longa" e "Media Intermediaria"

#### Scenario: Otimização de Risco AXS
- DADO que o usuário está na página `/optimize/risk`
- QUANDO ESTRATEGIAAXS é selecionada
- ENTÃO é possível configurar faixas de Stop Loss e Take Profit para a estratégia

#### Scenario: Stop Loss em ESTRATEGIAAXS
- DADO que ESTRATEGIAAXS é selecionada para backtest
- QUANDO o usuário configura um Stop Loss (ex: 2%)
- ENTÃO a estratégia respeita o stop loss nas operações executadas

### Requirement: Visualização de Indicadores ESTRATEGIAAXS
O gráfico de resultados SHALL exibir as linhas das médias móveis da ESTRATEGIAAXS.
As linhas MUST usar cores: Curta (Vermelho), Longa (Azul), Intermediaria (Laranja).

#### Scenario: Visualizar Médias AXS no Gráfico
- DADO que um backtest com ESTRATEGIAAXS foi executado
- QUANDO o usuário visualiza o gráfico de resultados
- ENTÃO três linhas representando as médias são exibidas nas cores corretas
