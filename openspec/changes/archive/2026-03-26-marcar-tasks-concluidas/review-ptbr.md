# Revisão PO — Card #50: Marcar Tasks Concluídas

## Resumo

**Card:** #50 — "marcar-tasks-concluidas"  
**Problema:** O sistema exibe tasks de `tasks.md` no Kanban, mas não permite marcá-las como concluídas pela interface. A única forma era editar o arquivo manualmente.  
**Solução:** Adicionar clique no checkbox da TaskTree que atualiza tanto a DB quanto o `tasks.md`.

---

## O que foi criado

### Artefatos OpenSpec

| Artefato | Caminho |
|----------|---------|
| `.openspec.yaml` | `openspec/changes/marcar-tasks-concluidas/.openspec.yaml` |
| `proposal.md` | `openspec/changes/marcar-tasks-concluidas/proposal.md` |
| `design.md` | `openspec/changes/marcar-tasks-concluidas/design.md` |
| `tasks.md` | `openspec/changes/marcar-tasks-concluidas/tasks.md` |
| `review-ptbr.md` | `openspec/changes/marcar-tasks-concluidas/review-ptbr.md` |

---

## Escopo da Solução

### Backend (2 tarefas principais)
1. **Service:** Nova função `toggle_task_checkbox(change_id, task_code, checked)` em `change_tasks_service.py`
   - Localiza a linha da task em `tasks.md` via regex no `task_code`
   - Substitui `- [ ]` ↔ `- [x]`
   - Preserva indentação original

2. **Endpoint:** Modificar `PATCH /workflow/work-items/{work_item_id}` em `workflow.py`
   - Após atualizar DB, chama `toggle_task_checkbox`
   - Extrai `task_code` do campo `description` (formato: `code:1.1`)
   - Faz rollback da transação se escrita no arquivo falhar

### Frontend (2 tarefas principais)
1. **TaskTree interativo:** Checkbox clicável com `onClick` → `PATCH /workflow/work-items/{id}`
2. **Mapa task_code → work_item_id:** Resolver ID do work item para enviar no request

---

## Critérios de Aceitação

- [ ] Checkbox clicável na interface
- [ ] Arquivo `tasks.md` atualizado (`- [ ]` → `- [x]`)
- [ ] Reversão funcional (volta para `- [ ]`)
- [ ] Estado persiste após reload
- [ ] DB atualizada com `state: done`

---

## Fora do Escopo

- Criação de tasks via UI (outro card)
- Bulk update de tasks
- Histórico de mudanças

---

## Próximo Passo

Alan aprova → passa para DEV implementar.
