# Proposal — orden-execu-o-dos-cards

## Why

Hoje o Kanban mostra os cards por coluna, mas não oferece um jeito explícito de definir a **ordem de execução** dentro da própria fila.

Sem isso, a prioridade fina entre cards da mesma etapa fica ambígua: os agentes não têm um sinal operacional claro de qual item deve ser puxado primeiro, e o board acaba servindo só como estágio, não como fila ordenada.

## What changes

Esta change adiciona ordenação manual de cards dentro do board para que a posição visual represente a ordem operacional de pull:
- mover um card **para cima** ou **para baixo** dentro da coluna
- persistir essa ordem no runtime/workflow DB
- refletir imediatamente a nova posição no Kanban
- deixar claro que agentes devem puxar primeiro os itens mais prioritários na ordem visível da coluna

## In scope
- ordenação manual intra-coluna no Kanban
- persistência da ordem no runtime/workflow DB
- regra operacional de leitura da fila pelos agentes
- atualização imediata do board após reordenação
- cobertura de validação básica para manter ordenação consistente

## Out of scope
- reorder arbitrário entre colunas sem respeitar gates
- priorização automática por IA
- ranking global cruzando múltiplas colunas
- mudança no modelo de aprovação/gates
- edição de outros metadados do card (coberta por outra change)

## Capabilities

### New capabilities
- `kanban-card-ordering`: reordenar cards manualmente dentro da mesma coluna
- `workflow-queue-priority`: persistir prioridade posicional do card como fonte operacional de pull order

### Modified capabilities
- `kanban`: passa a expressar prioridade fina via ordem visual dos cards por coluna
- `workflow-state-db`: passa a armazenar e devolver ordem estável para cards na mesma etapa

## Impact
- Frontend: UI do Kanban para mover card para cima/baixo ou equivalente de reorder
- Backend: endpoints/serviços para persistir a ordem por coluna
- Runtime data model: campo/estratégia de ordenação por estágio/coluna
- Tests: backend + frontend/E2E cobrindo reorder e persistência visual

## Success criteria
- Alan consegue mudar a ordem de dois cards da mesma coluna direto no board
- a ordem persiste após refresh/leitura posterior
- a coluna passa a representar prioridade operacional explícita
- agentes conseguem consultar a fila ordenada sem ambiguidade
