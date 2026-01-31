# Favorites Capability

## ADDED Requirements

### Requirement: Salvar Estratégia dos Resultados do Combo
O sistema DEVE (MUST) fornecer um mecanismo para salvar uma configuração específica de estratégia (incluindo parâmetros e métricas) da página de Resultados do Backtest de Combo para a lista de Favoritos.

#### Scenario: Usuário salva uma estratégia de alto desempenho
DADO que o usuário executou um backtest ou otimização em `/combo/select`
E os resultados mostram uma estratégia de alto desempenho (ex: ROI > 1000%)
QUANDO o usuário clica no botão "Salvar nos Favoritos"
E insere um nome descritivo no modal de confirmação
ENTÃO a configuração da estratégia E suas métricas de desempenho são salvas na lista persistida de Favoritos
E o usuário recebe uma notificação de sucesso.

#### Cenário: Evitar Duplicatas
DADO que o usuário tenta salvar uma estratégia com o mesmo nome de um favorito existente
QUANDO ele clica em salvar
ENTÃO o sistema DEVE (MUST) exibir um aviso perguntando se deseja sobrescrever ou salvar como novo
OU impedir a ação com uma mensagem de erro clara.

### Requirement: Campo de Notas
O modal de salvamento DEVE (MUST) incluir um campo opcional para "Notas" (observações), que será persistido no banco de dados junto com a estratégia.

#### Scenario: Usuário adiciona contexto
DADO que o usuário está salvando uma estratégia
QUANDO ele digita "Melhor resultado em mercado de alta" no campo de Notas
ENTÃO essa observação é salva e exibida na lista de Favoritos junto com a estratégia.

### Requirement: Armazenar Métricas Compostas
O sistema DEVE (MUST) armazenar a métrica `total_return` como o valor de Retorno Composto (Crescimento Real do Portfólio) ao salvar nos Favoritos.

#### Scenario: Consistência de Métricas
DADO que um resultado de backtest mostra um Retorno Total de 24.000% (Composto)
QUANDO a estratégia é salva nos Favoritos
ENTÃO o Painel de Favoritos DEVE exibir o mesmo retorno de 24.000%
E NÃO DEVE exibir o retorno de Soma Simples (ex: 6.000%).
