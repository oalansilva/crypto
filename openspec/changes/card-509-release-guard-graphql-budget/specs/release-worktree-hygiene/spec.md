## ADDED Requirements

### Requirement: Snapshot remoto único por execução
O release guard SHALL carregar no máximo uma fotografia completa do GitHub Project e uma fotografia global de pull requests abertos por execução, reutilizando esses dados em todos os checks do mesmo processo e sem reutilizá-los em execuções futuras.

#### Scenario: Múltiplas branches e checks dependem do board
- **WHEN** uma execução avalia changes terminais, branches, campos do pacote e evidência de homologação
- **THEN** o guard realiza no máximo uma listagem completa do Project e resolve as consultas restantes localmente

#### Scenario: Nova execução começa
- **WHEN** o release guard é iniciado novamente após uma execução anterior
- **THEN** o guard obtém uma nova fotografia autoritativa e não aceita cache persistente da execução anterior

### Requirement: Snapshot completo é condição de validade
O snapshot do Project SHALL ser válido somente se `.items` for array e a quantidade de itens corresponder a `totalCount` informado pela API. A listagem global de pull requests SHALL ser considerada truncada quando atingir o limite configurado. Snapshot truncado ou incompleto produz estado desconhecido.

#### Scenario: Board maior que o retornado
- **WHEN** a quantidade de itens retornada é menor que `totalCount`
- **THEN** o guard trata o snapshot como inválido e não resolve decisões a partir dele

#### Scenario: Listagem de PRs atinge o limite
- **WHEN** a listagem de pull requests retorna o número máximo de itens configurado
- **THEN** o guard trata a fotografia de PRs como truncada e desconhecida

### Requirement: Estado remoto desconhecido é explícito e fail-closed
O release guard MUST distinguir estado terminal, não terminal e desconhecido para cards e pull requests. Falha de API, JSON inválido, card ausente ou duplicado, Status ausente e resultado remoto ambíguo SHALL produzir estado desconhecido. A falha de um snapshot SHALL ser tratada de forma única e global, independentemente de consumidores ativos.

#### Scenario: Consulta remota falha no modo post
- **WHEN** o snapshot do Project ou de pull requests não pode ser carregado ou validado em `post`
- **THEN** o guard registra blocker com causa explícita e termina com falha

#### Scenario: Consulta remota falha no modo audit
- **WHEN** o snapshot do Project ou de pull requests não pode ser carregado ou validado em `audit`
- **THEN** o guard registra warning explícito e não representa o estado como válido

#### Scenario: Snapshot falha sem consumidores relevantes
- **WHEN** o snapshot falha e nenhuma branch ou card do pacote dependeria dele na seção atual
- **THEN** a falha ainda é reportada de forma global e imediata conforme o modo (blocker em `post`, warning em `audit`)

#### Scenario: Card não terminal existe no snapshot
- **WHEN** exatamente um card possui o número esperado e seu Status não é `Pronto` nem `Cancelado`
- **THEN** o guard classifica o card como não terminal sem tratá-lo como falha remota

### Requirement: Pacote de release referencia cards inequívocos
O release guard MUST normalizar `RELEASE_CARDS` uma única vez — trim de espaços, remoção de zeros à esquerda, deduplicação e validação numérica no intervalo 1..2147483647 — e confirmar que cada ID normalizado aparece exatamente uma vez no snapshot do Project e possui Status antes de validar campos obrigatórios ou evidência de homologação.

#### Scenario: Formato inválido no pacote
- **WHEN** `RELEASE_CARDS` contém token não numérico, vazio ou fora do intervalo
- **THEN** o modo estrito falha antes de qualquer consulta remota

#### Scenario: Card do pacote está ausente ou duplicado
- **WHEN** um ID normalizado de `RELEASE_CARDS` não aparece ou aparece mais de uma vez no snapshot
- **THEN** o modo estrito falha e identifica o card ambíguo ou ausente

#### Scenario: IDs canonicamente duplicados são aceitos
- **WHEN** `RELEASE_CARDS` contém `480, 0480`
- **THEN** o guard deduplica para um único card `480` e o valida uma vez

#### Scenario: Cards do pacote são inequívocos
- **WHEN** todos os IDs normalizados aparecem exatamente uma vez e possuem Status
- **THEN** o guard reutiliza os mesmos itens para validar campos e homologação

### Requirement: Diagnóstico de limite GraphQL sem retry loop
Quando uma consulta de Project falhar, o release guard SHALL consultar o rate limit disponível e incluir saldo GraphQL e reset na mensagem quando esses dados puderem ser obtidos, sem polling, espera ou nova tentativa automática da consulta completa.

#### Scenario: Project falha por cota insuficiente
- **WHEN** a listagem do Project falha e o endpoint de rate limit informa saldo e reset
- **THEN** o guard reporta esses valores e mantém a falha conforme o modo atual

### Requirement: Paginação de idade respeita limite total
O inventário de idade em `audit` MUST contar a página inicial no limite total configurado de páginas GraphQL.

#### Scenario: Board possui mais páginas que o limite
- **WHEN** a paginação informa novas páginas após atingir o limite total
- **THEN** o guard encerra a paginação sem realizar uma requisição adicional
