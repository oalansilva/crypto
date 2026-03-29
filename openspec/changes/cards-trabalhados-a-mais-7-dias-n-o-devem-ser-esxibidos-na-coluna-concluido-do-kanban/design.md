---
spec: openspec.v1
id: cards-trabalhados-a-mais-7-dias-n-o-devem-ser-esxibidos-na-coluna-concluido-do-kanban
title: Design - Ocultar Cards Antigos
card: "#62"
change_id: hide-old-completed-cards
stage: DESIGN
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Design: Ocultar Cards Antigos na Coluna Concluído

**Card:** #62  
**change_id:** `hide-old-completed-cards`

---

## Solução

Filtrar no frontend (ou backend) cards onde `completed_at` (ou `updated_at`) é maior que 7 dias.

### Lógica

```
hoje - 7 dias = data_limite
SE card.completed_at < data_limite ENTÃO não exibir na coluna Done
```

### Opção: Link de Histórico

Opcionalmente, mostrar um link "Ver histórico" que revela cards antigos.

---

## Implementação

1. Adicionar filtro na query de cards da coluna Done
2. Filtrar por `completed_at` ou `updated_at` com threshold de 7 dias
3. Se implementado link de histórico: endpoint ou toggle no frontend

---

## Próximo Passo

Após DESIGN, passar para DEV.
