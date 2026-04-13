# Review PT-BR — Card #88

## Resumo

**Card:** #88 — Remover Funcionalidade Kanban  
**Projeto:** crypto  
**Mudar:** Remover rota `/kanban` e navegação relacionada do projeto crypto

---

## O que é

Remoção de funcionalidade: eliminar a integração do Kanban standalone no projeto crypto. Usuários que acessavam Kanban via `/kanban` no crypto precisarão usar o app Kanban standalone diretamente.

---

## Decisão Necessária

**Sim** — precisamo confirmar:

1. **Comunicação aos usuários** — como avisar usuários da mudança?
2. **URL do Kanban standalone** — qual é a URL do app Kanban para redirecionar usuários?
3. **Timeline** — remoção imediata ou gradual?

---

## Tradeoffs

| | Prós | Contras |
|---|---|---|
| **Remover** | Código mais limpo, menos manutenção | Usuários perdem acesso convenience |
| **Manter** | Convenience para usuários | Mais código para manter |

---

## Próximo Passo

**Alan approval** → DEV implementation

**Nota:** Por ser remoção de UI (navegação), DESIGN deve validar que a navegação fica correta após remoção.

---

## Artefatos

- `openspec/changes/remover-funcionalidade-kaban/proposal.md`
- `openspec/changes/remover-funcionalidade-kaban/review-ptbr.md`
- `openspec/changes/remover-funcionalidade-kaban/tasks.md`
