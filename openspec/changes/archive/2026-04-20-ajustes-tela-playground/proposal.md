# Proposal: Ajustes Tela Playground - Remover Referências ao Kanban

## User Story

**Como** usuário do crypto  
**Eu quero** não ver mais referências ao Kanban na tela de playground  
**Para** que a interface seja consistente e não confunda

---

## Problem Statement

Após a remoção da funcionalidade Kanban (card #88), ainda existem referências residuais na tela de playground:
- "Abrir Kanban" — botão/link para abrir Kanban
- "Kanban Real" — configuração ou texto relacionado

Essas referências não funcionam mais e confundem o usuário.

---

## Scope In

- Remover texto/botões "Abrir Kanban" da tela playground
- Remover "Kanban Real" da tela playground
- Buscar e remover outras referências ao Kanban na mesma tela
- Verificar se há referências em outras telas relacionadas

---

## Scope Out

- Não afeta funcionalidades do playground que não sejam relacionadas a Kanban
- Não remove funcionalidades de outros projetos

---

## References to Remove

| Referência | Tipo | Localização Provável |
|------------|------|---------------------|
| "Abrir Kanban" | Botão/Link | PlaygroundScreen.tsx |
| "Kanban Real" | Texto/Config | PlaygroundScreen.tsx ou settings |

**Nota:** Buscar por variantes: "kanban", "Kanban", "Kaban"

---

## Technical Approach

1. **Buscar no frontend** por "kanban", "Kanban", "Kaban"
2. **Identificar componentes** que renderizam essas referências
3. **Remover ou comentar** o código relacionado
4. **Verificar navegação** — garantir que links para /kanban foram removidos

---

## Dependencies

- **Card #88** (remover funcionalidade kaban) — contexto: este card limpa resíduos deixados pelo #88

---

## Risks

1. **Baixo** — Remoção de texto/UI simples
2. **Links órfãos** — se houver roteamento via código, pode quebrar
3. **Referências em cascata** — pode haver mais telas com resíduos

---

## ICE Score

- Impact: 5 (limpeza de UI, não impacta funcionalidade)
- Confidence: 8 (escopo claro)
- Ease: 9 (remoção simples de texto)
- **ICE: 360**
