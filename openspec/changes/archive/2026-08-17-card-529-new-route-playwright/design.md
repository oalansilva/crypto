## Context

Rota nova em `App.tsx` não quebra o pipeline se ninguém escreveu spec. #469 passou assim. A regra 13 é voluntária.

## Goals / Non-Goals

**Goals:**
- Check fail-closed: rota nova sem spec → job vermelho + `qa-gate` vermelho.
- Spec cobre desktop/mobile com snapshots.
- Dispensa só com label + comentário Alan.
- Inventário das rotas atuais para não falhar o legado de uma vez.

**Non-Goals:**
- Reescrever todas as telas antigas sem spec neste card (grandfather).
- Specs de `frontend/public/prototypes/` (#568).

## Decisions

1. **Parser estático de `App.tsx`**, não runtime. Extrair `path="..."` de rotas de produto (páginas). Excluir `PrototypeRedirect`, paths `/prototypes/*`, `Navigate` de alias (`/kanban`, `/preferences`, index) — aliases contam como cobertos pelo destino.
2. **Rota nova = path de produto que não está no inventário.** PR que adiciona rota de página precisa adicionar spec **e** atualizar o inventário no mesmo diff.
3. **Matching por convenção:** path `/combo/discovery` espera spec que declare a rota (grep do path ou campo no inventário). Não exigir nome de arquivo mágico se o inventário aponta o spec.
4. **UI impact: none.** Check de CI, sem tela.

## UI impact

`none` — tooling/CI. Nenhuma superfície de produto neste card.

## Prototype

N/A. Justificativa: o entregável é o check vermelho, não uma tela.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Risks / Trade-offs

- [Falsos positivos em `Navigate` / rotas alias] → Inventário inclui redirects (`/kanban` → `/monitor`) como cobertos pelo destino ou como grandfather.
- [Spec existe mas não visita a rota] → Inventário exige o path no spec; check grep `goto`/`path` no arquivo apontado.
- [Carga de snapshots para rota nova] → Aceito: é o objetivo do card.

## Migration Plan

1. OpenSpec + aprovação.
2. Gerar inventário das rotas atuais + specs existentes.
3. Script + job CI + docs.
4. Teste: adicionar rota fake em fixture deve falhar o script.

## Open Questions

Nenhuma.

## Design Critique

- Escopo: check de CI de rota nova; sem tela.
- Crítica isolada: P1 de `PrototypeRedirect`/`Navigate` corrigido — aliases e `/prototypes/*` ficam de fora.
- Superfície visual nova: nenhuma.

## Prototype Validation

N/A — sem protótipo navegável.

Design Agent verdict: PASS
