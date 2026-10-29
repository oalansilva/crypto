## ADDED Requirements

### Requirement: process_event move pelo executor quando o overlay o declara
Quando o overlay declarar `board.executor`, `process_event` SHALL mover o Status só por pedido `pedir` ao executor, com evento, card, `de` (Status visto), ator (`Agent`, ou `Guard` em T17a/T17b), cliente, sessão e extras (`digest` no T5, um pedido por card do pacote no T16). Recusa do executor SHALL virar `reject` com `reason=executor:<motivo>` e Status inalterado. Nesse modo, `process_event` MUST NOT chamar `gh project item-edit` nem GraphQL de escrita no Project. Os eventos do Alan SHALL continuar recusados localmente com `reason=actor`, sem pedido ao executor. Unit tests SHALL injetar um executor falso e MUST NOT chamar o GitHub.

#### Scenario: Transição do agente pelo executor
- **WHEN** `process_event pedir_review` é avaliado como `transition` com `board.executor` no overlay
- **THEN** o executor falso recebe um pedido `pedir` com `evento=pedir_review`, `de=Em desenvolvimento` e `ator=Agent`
- **AND** nenhum `item-edit` é chamado

#### Scenario: Executor recusa
- **WHEN** o executor falso responde `recusado: no_edge` a um pedido de `aceitar_sha`
- **THEN** `process_event` devolve `reject` com `reason=executor:no_edge` e o Status fica igual

#### Scenario: T5 leva o digest
- **WHEN** `process_event submeter_design` faz a transição
- **THEN** o pedido ao executor traz o `digest` calculado por `compute_digest` do `design.md` e do protótipo do card

### Requirement: criar_card põe o issue no board pelo executor
Com `board.executor` no overlay, `process_event criar_card --card N` SHALL pedir ao executor que ponha o issue N, que já existe, no Project 1 em Em Refinamento. Issue inexistente ou já presente no board MUST ser recusado com o motivo.

#### Scenario: Card novo do Kaizen
- **WHEN** o orquestrador cria o issue N e roda `process_event criar_card --card N`
- **THEN** o issue N aparece no board em Em Refinamento, pelo executor
