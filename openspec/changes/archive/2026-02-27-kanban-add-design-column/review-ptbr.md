# Revisão (PT-BR) — kanban-add-design-column

## Objetivo
Atualizar o Kanban pra refletir o novo fluxo com etapa **DESIGN**.

## Mudança
- Adicionar coluna **DESIGN** sempre visível entre **PO** e **Alan approval**:
  **PO → DESIGN → Alan approval → DEV → QA → Homologation → Archived**

## Regra
- Coordination passa a suportar o campo `DESIGN:` com estados: `not started | in progress | blocked | done | skipped`.
- Se `DESIGN: skipped`, a change segue para `Alan approval` normalmente.

## Próximo passo
Tu aprovar (“ok”) pra eu implementar.
