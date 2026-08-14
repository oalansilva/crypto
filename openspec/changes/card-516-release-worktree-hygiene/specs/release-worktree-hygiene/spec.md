## ADDED Requirements

### Requirement: Estado remoto desconhecido nunca constitui preservação válida

Quando o snapshot do Project estiver ausente, inválido, incompleto ou em estado `failed`, o release guard MUST preservar o resultado de lookup como `unknown` e MUST NOT classificar qualquer branch dependente desse lookup como `preserved`, `card in flight` ou outro estado de negócio conhecido. O modo `post` MUST registrar blocker e terminar sem sucesso; o modo `audit` SHALL registrar warning explícito e continuar apenas como diagnóstico.

#### Scenario: Snapshot falha durante post com branch inventariada

- **WHEN** o fake `gh` faz o snapshot do Project falhar e existe uma branch cujo status dependeria do board
- **THEN** `post` retorna não zero com blocker da falha do snapshot e a saída não classifica essa branch como `preserved` nem `card in flight`

#### Scenario: Snapshot falha durante audit com branch inventariada

- **WHEN** a mesma falha ocorre em `audit`
- **THEN** o guard emite warning explícito de estado remoto desconhecido e a saída não classifica a branch como `preserved` nem `card in flight`

#### Scenario: Card conhecido está realmente em fluxo

- **WHEN** o snapshot é autoritativo e o card da branch possui Status conhecido não terminal
- **THEN** a classificação `preserved (card in flight; not deleted)` continua permitida

### Requirement: Limpeza de branches do pacote usa manifest e prova por ref

O closeout SHALL registrar o manifest nominal completo de branches do pacote antes da limpeza. Para cada branch, o executor MUST registrar o tip local/remoto disponível e MUST provar integração por ancestralidade, equivalência de árvore, equivalência de patch ou ausência de diff material nos arquivos tocados. Branch não integrada MUST NOT ser removida sem autorização humana explícita vinculada ao nome e à evidência comparada. Branch com worktree ativa MUST permanecer bloqueada para deleção.

#### Scenario: Branch integrada pode ser removida

- **WHEN** uma branch do manifest não possui worktree ativa e sua integração é provada contra `origin/develop`
- **THEN** as refs local e remota podem ser removidas e sua ausência é verificada depois de atualizar/prunar as refs

#### Scenario: Branch marcada como not merged possui autorização

- **WHEN** a árvore e os patches exclusivos foram revisados e Alan autorizou explicitamente descartar a branch identificada por nome e tip
- **THEN** a deleção forçada pode ocorrer com a autorização e a prova pós-deleção registradas no handoff

#### Scenario: Contagem sem nomes não prova limpeza

- **WHEN** a auditoria histórica informa apenas que existem 17 branches pendentes, mas o manifest nominal não foi recuperado
- **THEN** o closeout permanece incompleto mesmo que as branches conhecidas não apareçam em `git branch -a`

### Requirement: Medição GraphQL é vinculada a uma execução identificada

A evidência de orçamento SHALL registrar commit do guard, modo, horário, saldo GraphQL antes e depois e resultado terminal de uma única execução. O delta observado MUST ser de no máximo aproximadamente 500 pontos para satisfazer este card. Consumo concorrente conhecido ou não separável SHALL tornar a medição inconclusiva, e o executor MUST NOT repetir silenciosamente o run para selecionar um delta menor.

#### Scenario: Execução isolada permanece no orçamento

- **WHEN** uma execução identificada ocorre sem consumidor concorrente conhecido e o saldo GraphQL cai em até aproximadamente 500 pontos
- **THEN** o handoff registra o delta, a referência histórica de aproximadamente 4.900 pontos e o resultado do guard

#### Scenario: Cota sofre consumo concorrente

- **WHEN** outra automação usa a mesma credencial durante a janela e o delta não pode ser atribuído ao guard
- **THEN** a medição é registrada como inconclusiva e não conta como aceite do orçamento
