---
spec: openspec.v1
id: quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54
title: Tasks - Localizar Card pelo Código
card: "#63"
change_id: find-card-by-code
stage: PO
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Tasks: Localizar Card pelo Código

**Card:** #63 | `find-card-by-code`

---

## Tarefas

### Frontend

- [ ] **T-001:** Adicionar campo de input no header do Kanban (ou atalho Ctrl+G)
- [ ] **T-002:** Detectar padrão `#` + número no input
- [ ] **T-003:** Ao digitar Enter ou perder foco, disparar busca
- [ ] **T-004:** Se card encontrado: scroll to card ou abrir modal
- [ ] **T-005:** Se card não encontrado: mostrar mensagem "Card #XX não encontrado"
- [ ] **T-006:** Tecla Esc fecha/foca fora do input

### Backend (se necessário)

- [ ] **T-007:** Endpoint ou função para buscar card por `card_number`

---

## Critérios de Conclusão

- [ ] Usuário pode digitar #54 e ir para o Card #54
- [ ] Se card não existe, mostra mensagem clara
- [ ] Atalho de teclado funciona (Ctrl+G)

---

## Dependencies

- Nenhuma
