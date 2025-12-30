# Spec: Performance Metrics

## ADDED Requirements

### Requirement: Calculate CAGR (Compound Annual Growth Rate)

O sistema deve calcular o CAGR para permitir comparação justa entre estratégias testadas em períodos diferentes.

**Fórmula**: `CAGR = (Final Value / Initial Value)^(1/Years) - 1`

#### Scenario: Backtest de 1 ano com 100% retorno

**Given** um backtest executado de 01/01/2023 a 31/12/2023  
**And** capital inicial de $10,000  
**And** capital final de $20,000  
**When** as métricas são calculadas  
**Then** o CAGR deve ser aproximadamente 100%

#### Scenario: Backtest de 2 anos com 100% retorno

**Given** um backtest executado de 01/01/2023 a 31/12/2024  
**And** capital inicial de $10,000  
**And** capital final de $20,000  
**When** as métricas são calculadas  
**Then** o CAGR deve ser aproximadamente 41.4%

#### Scenario: Backtest de período fracionário

**Given** um backtest executado por 6 meses  
**And** capital inicial de $10,000  
**And** capital final de $11,000  
**When** as métricas são calculadas  
**Then** o CAGR deve ser anualizado corretamente

### Requirement: Calculate Monthly Average Return

O sistema deve calcular o retorno médio mensal para avaliar consistência da estratégia.

#### Scenario: Retornos mensais consistentes

**Given** um backtest de 12 meses  
**And** retornos mensais de [5%, 4%, 6%, 5%, 5%, 4%, 6%, 5%, 4%, 5%, 6%, 5%]  
**When** as métricas são calculadas  
**Then** o retorno médio mensal deve ser 5%

#### Scenario: Retornos mensais voláteis

**Given** um backtest de 12 meses  
**And** retornos mensais de [20%, -10%, 15%, -5%, 25%, -15%, 10%, 5%, -8%, 12%, 8%, -7%]  
**When** as métricas são calculadas  
**Then** o retorno médio mensal deve refletir a média aritmética
**And** a volatilidade deve ser calculada separadamente

### Requirement: Display Performance Metrics in UI

O frontend deve exibir métricas de performance de forma clara e comparável.

#### Scenario: Exibição de métricas de performance

**Given** um backtest concluído com métricas calculadas  
**When** o usuário visualiza a página de resultados  
**Then** deve ver uma seção "Performance" contendo:
  - Retorno Total (%)
  - CAGR (%)
  - Retorno Médio Mensal (%)
**And** cada métrica deve ter um tooltip explicativo

#### Scenario: Comparação com benchmark

**Given** métricas de performance calculadas  
**And** métricas de benchmark (Buy & Hold) disponíveis  
**When** o usuário visualiza a seção de performance  
**Then** deve ver comparação lado-a-lado:
  - Estratégia vs Buy & Hold
  - Diferença (Alpha) destacada visualmente
