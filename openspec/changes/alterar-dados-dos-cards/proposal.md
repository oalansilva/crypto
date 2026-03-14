# Proposal — alterar-dados-dos-cards

## Why

Hoje o Kanban já permite criar e mover cards, mas ainda falta um ajuste operacional básico: conseguir corrigir o **título** e a **descrição** de um card depois que ele existe, além de conseguir **cancelar** um card que entrou por engano, duplicado ou perdeu sentido.

Sem isso, pequenas correções de cadastro dependem de intervenção fora do fluxo normal e cards inválidos continuam poluindo a fila ativa.

## What changes

Esta change adiciona um fluxo simples e seguro para manutenção de cards no próprio Kanban:
- editar **title** e **description** de uma change/card existente
- permitir **cancelamento explícito** do card sem apagar histórico
- refletir essas mudanças imediatamente no runtime/Kanban
- manter trilha operacional via comments/handoffs e estado consistente no workflow DB

## In scope
- edição de título de card
- edição de descrição de card
- ação de cancelamento de card/change no fluxo de Kanban
- persistência no workflow DB
- atualização visual do board/drawer após salvar
- regras mínimas para impedir cancelamento destrutivo/silencioso

## Out of scope
- exclusão física de cards
- edição arbitrária de gates/approvals pelo mesmo fluxo
- bulk edit de múltiplos cards
- redefinição do modelo de work items (`change` / `story` / `bug`)
- reordenação de cards no board (coberta por outra change)

## Capabilities

### New capabilities
- `kanban-card-editing`: editar título e descrição de cards já existentes a partir do Kanban/detalhe do card
- `kanban-card-cancelation`: cancelar um card sem removê-lo do histórico operacional

### Modified capabilities
- `kanban`: passa a oferecer manutenção básica de metadados do card além de criação/movimentação
- `workflow-state-db`: passa a suportar cancelamento explícito sem exigir remoção física do registro

## Impact
- Frontend: `frontend/src/pages/KanbanPage.tsx` e componentes/estado relacionados ao drawer/modal de card
- Backend: rotas workflow/kanban para update de change e política de cancelamento
- Runtime data model: reaproveitar status/approvals/work items sem perda de rastreabilidade
- Tests: backend + frontend/E2E cobrindo edição e cancelamento

## Success criteria
- Alan consegue editar título/descrição de um card existente direto no Kanban
- um card cancelado sai do fluxo ativo sem ser apagado do histórico
- a UI reflete a edição/cancelamento sem reload manual
- a trilha operacional permanece auditável no runtime/Kanban
