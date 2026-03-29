---
spec: openspec.v1
id: quero-conseguir-localizar-e-carregar-um-card-facilmente-pelo-codigo-ex-54
title: Design - Localizar Card pelo Código
card: "#63"
change_id: find-card-by-code
stage: DESIGN
status: draft
owner: Alan
created_at: 2026-03-27
updated_at: 2026-03-27
---

# Design: Localizar Card pelo Código

**Card:** #63  
**change_id:** `find-card-by-code`

---

## Solução

### Input de Busca

Campo de texto no header do Kanban ou atalho de teclado (ex: Ctrl+G / Cmd+G).

### Comportamento

1. Usuário digita `#54`
2. Sistema detecta padrão `#` + número
3. Ao pressionar Enter ou ao digitar, busca card por `card_number`
4. Se encontrado: abre modal ou rola até o card
5. Se não encontrado: mostra "Card #XX não encontrado"

### Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| Ctrl+G | Focar campo de busca |
| Enter | Buscar card digitado |
| Esc | Fechar/fechar modal |

---

## Implementação

1. Adicionar campo de input no Header do Kanban
2. Listener para detectar `#` + números
3. Query no backend por `card_number`
4. UI para exibir card encontrado (scroll to ou modal)

---

## Próximo Passo

Após DESIGN, passar para DEV.
