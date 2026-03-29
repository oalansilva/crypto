---
spec: openspec.v1
id: cards-trabalhados-a-mais-7-dias-n-o-devem-ser-esxibidos-na-coluna-concluido-do-kanban
title: Ocultar Cards Antigos na Coluna Concluído
card: "#62"
change_id: hide-old-completed-cards
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Proposal: Ocultar Cards Antigos na Coluna Concluído

**Card:** #62  
**change_id:** `hide-old-completed-cards`

---

## Resumo

Cards marcados como concluído há mais de 7 dias não devem ser exibidos na coluna "Concluído" do Kanban. Cards mais antigos são automaticamente escondidos para manter a visualização limpa.

## User Story

> Como usuário do Kanban, quero que cards antigos (mais de 7 dias) não apareçam na coluna Concluído para manter o board limpo e focado.

---

## Escopo

### Dentro do escopo
- [ ] Filtrar cards com `updated_at` ou data de conclusão > 7 dias da coluna Done
- [ ] Manter link/acesso ao histórico de cards antigos (opcional)

### Fora do escopo
- [ ] Excluir ou arquivar cards
- [ ] Mover cards automaticamente

---

## Próximo Passo

Passar para DESIGN para especificação de implementação.
