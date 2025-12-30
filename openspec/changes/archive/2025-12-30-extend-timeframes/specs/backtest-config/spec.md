# Configuração de Backtest

## ADDED Requirements

### Requirement: Suporte a Backtesting de Período Completo

O sistema DEVE (MUST) permitir que os usuários selecionem facilmente "Todos os dados disponíveis" sem escolher datas manualmente.

#### Scenario: Usuário seleciona Período Completo
Given que o usuário está no Wizard de Backtest
When ele marca o checkbox "Todo o período"
Then os inputs de "Data Inicial" e "Data Final" devem ser desabilitados
And a requisição de backtest deve ser enviada com `full_period=true`
And o backend deve buscar dados começando da data viável mais antiga (ex: 2017-01-01)

#### Scenario: Backend trata data de início opcional
Given uma requisição de backtest com `full_period=true`
When o backend processa a requisição
Then ele deve ignorar qualquer data `since` fornecida
And ele deve definir o padrão de `since` para "2017-01-01 00:00:00"
And `until` deve ser definido para o tempo atual (ou None)
