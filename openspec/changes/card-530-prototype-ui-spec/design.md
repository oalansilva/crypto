## Context

No #469 o DEV tratou o contrato de API como spec de UI. O protótipo aprovado existia e não foi aberto. Este card muda o apply/review, não a tela Discovery.

## Goals / Non-Goals

**Goals:**
- Apply `UI impact: affected` carrega `design.md` + protótipo HTML como spec de layout.
- Handoff registra consulta e elementos seguidos.
- Desvios explícitos; comparação pré-Code Review.
- Docs + kaizen-log (#469).

**Non-Goals:**
- Reimplementar Discovery (#469 Pronto).
- CI de rota nova (#529).
- Evidência por task no verify (#531).

## Decisions

1. **Skill apply ganha passo obrigatório** antes de editar `frontend/src` de produto.
2. **API ≠ layout.** Specs de endpoint continuam para dados.
3. **UI impact: none** neste card (processo).

## UI impact

`none` — skills/docs. Nenhuma tela de produto muda aqui.

## Prototype

N/A. Justificativa: o card não entrega UI; entrega regra de apply. O protótipo do #469 é evidência histórica, não superfície deste card.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Risks / Trade-offs

- [Agente ignora a skill] → #531/#529 pegam a falha no verify/CI; este card ataca a causa no apply.
- [Protótipo desatualizado vs tela] → Desvio tem que ser escrito; não autoriza inventar layout.

## Migration Plan

1. Aprovação de Design.
2. Atualizar skill apply, AGENTS, rules, kaizen-log.
3. QA visual: baseline inalterada.

## Open Questions

Nenhuma.

## Design Critique

- Escopo: skill `/opsx:apply` usa protótipo como spec de layout.
- Crítica isolada: PASS. Sem UI de produto neste card.
- Superfície visual nova: nenhuma.

## Prototype Validation

N/A — sem protótipo navegável.

Design Agent verdict: PASS
