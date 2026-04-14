# Review PT-BR — Card #91

## Resumo

**Card:** #91 — Ajustes Tela Playground  
**Projeto:** crypto  
**Mudar:** Remover referências residuais ao Kanban da tela de playground

---

## O que é

Card de **limpeza de UI** após a remoção da funcionalidade Kanban (card #88).

**Referências a remover:**
- "Abrir Kanban" — botão que não funciona mais
- "Kanban Real" — texto/config órfão

---

## Contexto

- Card #88 removeu a rota `/kanban` e navegação do projeto crypto
- Este card limpa os resíduos deixados na tela de playground

---

## Tradeoffs

| | Prós | Contras |
|---|---|---|
| **Remover** | UI limpa, sem confusão | Não há contra |
| **Manter** |用户提供清晰的操作界面 | 用户体验 |

---

## Próximo Passo

**Alan approval** → DEV implementation

---

## Artefatos

- `openspec/changes/ajustes-tela-playground/proposal.md`
- `openspec/changes/ajustes-tela-playground/review-ptbr.md`
- `openspec/changes/ajustes-tela-playground/tasks.md`
