---
spec: openspec.v1
id: cards-trabalhados-a-mais-7-dias-n-o-devem-ser-esxibidos-na-coluna-concluido-do-kanban
title: Tasks - Ocultar Cards Antigos
card: "#62"
change_id: hide-old-completed-cards
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Tasks: Ocultar Cards Antigos

**Card:** #62 | `hide-old-completed-cards`

---

## Tarefas

- [ ] **T-001:** Adicionar filtro de data na query de cards da coluna Done (backend ou frontend)
- [ ] **T-002:** Calcular threshold: hoje - 7 dias
- [ ] **T-003:** Excluir da listagem cards com completed_at < threshold
- [ ] **T-004:** (Opcional) Criar link/botão "Ver histórico" para mostrar cards antigos
- [ ] **T-005:** Testar com cards de diferentes datas

---

## Critérios de Conclusão

- [ ] Cards concluídos há mais de 7 dias não aparecem na coluna Done
- [ ] Cards novos ainda aparecem normalmente
- [ ] (Opcional) Histórico acessível via link

---

## Dependencies

- Nenhuma
