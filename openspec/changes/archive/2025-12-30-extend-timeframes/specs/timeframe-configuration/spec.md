# Configuração de Timeframe

## ADDED Requirements

### Requirement: Suporte a Timeframes Granulares Estendidos

O sistema DEVE (MUST) suportar timeframes adicionais para permitir backtesting e otimização mais granulares.

#### Scenario: Usuário seleciona timeframe de 5m
Given que o usuário está no Wizard de Backtest
When ele abre o dropdown de Timeframe
Then ele deve ver "5m" e "2h" como opções
And selecionar "5m" deve configurar o backtest para rodar com candles de 5 minutos

#### Scenario: Usuário seleciona timeframe de 2h
Given que o usuário está no Wizard de Backtest
When ele abre o dropdown de Timeframe
Then ele deve ver "2h" como opção
And selecionar "2h" deve configurar o backtest para rodar com candles de 2 horas
