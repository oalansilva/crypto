# Revisão (PT-BR) — kanban-visual-coordination

## Objetivo
Criar um **Kanban visual dentro do app** pra tu acompanhar o fluxo e as tasks/comentários.

## O que vai ter
- Página **`/kanban`**
- Colunas do nosso fluxo:
  - PO
  - Alan approval
  - DEV
  - QA
  - Alan homologation
  - Archived (sempre visível)
- Ao clicar num card:
  - checklist das tasks (lidas do `openspec/changes/<change>/tasks.md`)
  - comentários por change (thread)

## Fonte da verdade
- Status continua vindo dos arquivos `docs/coordination/<change>.md`
- Tasks continuam vindo do OpenSpec `tasks.md`

## Próximo passo
Tu aprovar (“ok”) o escopo pra eu implementar.
