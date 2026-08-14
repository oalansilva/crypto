# openspec archive hygiene Specification

## Purpose

Garantir que changes OpenSpec ativas de cards terminais sejam detectadas e arquivadas, inclusive quando o slug não contém id de card ou quando a change ainda possui artifacts/tasks pendentes.

## MODIFIED Requirements

### Requirement: Detecção de toda change ativa de card terminal no guard

O release guard SHALL, nos modos `post` e `audit`, enumerar toda change OpenSpec ativa e tentar associá-la a um card do repositório `oalansilva/crypto`. O vínculo SHALL usar primeiro um id presente no prefixo `card-<id>` ou `issue-<id>` e, na ausência desse id, um fallback determinístico por título que reutilize o snapshot completo do board e priorize os cards normalizados de `RELEASE_CARDS`. O guard MUST NOT exigir tasks ou artifacts completos para consultar a terminalidade. Uma change mapeada a card `Pronto` ou `Cancelado` SHALL ser reportada enquanto permanecer ativa, identificando se está `complete` ou `in-progress` e a fonte do mapeamento. `audit` SHALL emitir warning; `post` SHALL emitir blocker, incluindo obrigatoriamente qualquer change ativa de card do pacote. O fallback MUST NOT fazer consultas remotas por change e MUST tratar associação ambígua ou prova remota incompleta de forma fail-closed no modo estrito.

#### Scenario: Change completa com id no nome e card terminal

- **WHEN** uma change ativa `card-123-exemplo` possui todos os artifacts/tasks concluídos e o snapshot informa que o card #123 está em `Pronto` ou `Cancelado`
- **THEN** `audit` emite warning e `post` emite blocker com `progress=complete` e `mapping=name`

#### Scenario: Change in-progress com id no nome e card terminal

- **WHEN** uma change ativa `card-509-exemplo` possui task ou artifact pendente e o snapshot informa que o card #509 está terminal
- **THEN** a change não é descartada pelo progresso e o guard a reporta com `progress=in-progress`, como warning em `audit` e blocker em `post`

#### Scenario: Change sem id mapeada por título no pacote

- **WHEN** uma change ativa sem id no slug corresponde de forma única ao título de um card terminal listado em `RELEASE_CARDS`
- **THEN** o guard usa o snapshot já carregado, reporta `mapping=title` e aplica warning em `audit` ou blocker em `post`

#### Scenario: Diferença lexical entre slug e título

- **WHEN** o slug e o título usam verbos ou flexões diferentes, mas slug e proposal produzem uma correspondência única acima do limiar determinístico
- **THEN** o fallback associa a change ao card sem depender de referência numérica solta no conteúdo

#### Scenario: Associação por título é ambígua

- **WHEN** dois cards candidatos obtêm o mesmo melhor score ou nenhum alcança o piso de confiança
- **THEN** o guard não escolhe um card arbitrariamente; `audit` registra diagnóstico e `post` bloqueia quando a ambiguidade impede comprovar a higiene do pacote

#### Scenario: Card da change não é terminal

- **WHEN** a change é mapeada de forma inequívoca, mas o card está em estado diferente de `Pronto` e `Cancelado`
- **THEN** o guard não a reporta como change terminal nem exige archive por este check

#### Scenario: Todas as changes de cards terminais foram arquivadas

- **WHEN** não existe diretório ativo mapeado a card `Pronto` ou `Cancelado`
- **THEN** o guard informa ausência de changes terminais ativas sem warning ou blocker desta seção

#### Scenario: Orçamento remoto permanece constante

- **WHEN** várias changes sem id precisam do fallback por título na mesma execução
- **THEN** todas reutilizam `BOARD_JSON` e o número de chamadas de snapshot não cresce com a quantidade de changes

### Requirement: Change de card terminal deve ser arquivada

Uma change OpenSpec cujo card vinculado esteja em `Pronto` ou `Cancelado` SHALL ser removida da árvore ativa por archive canônico, independentemente de o guard classificá-la como `complete` ou `in-progress`. Changes completas SHALL seguir `/opsx:bulk-archive` com sync de delta specs quando aplicável. Uma change in-progress de card terminal SHALL exigir reconciliação/classificação explícita das pendências antes do archive, sem ser omitida do closeout.

#### Scenario: Change completa de card terminal

- **WHEN** uma change tem os artifacts/tasks concluídos e o card vinculado está terminal
- **THEN** ela é arquivada em `openspec/changes/archive/YYYY-MM-DD-<change>/` pelo fluxo OpenSpec aplicável

#### Scenario: Change in-progress de card terminal

- **WHEN** uma change tem task ou artifact pendente, mas o card vinculado já está terminal
- **THEN** o closeout é bloqueado até a pendência ser reconciliada e a change ser arquivada ou explicitamente classificada

#### Scenario: Change de card não terminal

- **WHEN** o card vinculado não está em `Pronto` nem `Cancelado`
- **THEN** a change permanece ativa e não é candidata a archive por este requisito
