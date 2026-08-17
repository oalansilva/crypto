## Context

No #469 tasks de UI foram `[x]` sem código e tasks Playwright ficaram `[ ]` em Done. Verify/review não cruzaram checklist × diff × protótipo.

## Goals / Non-Goals

**Goals:**
- `[x]` de UI exige evidência.
- Code Review tem checklist contra protótipo; falso `[x]` bloqueia commit.
- Verify registra comparação UI × protótipo.
- Task de teste `[ ]` bloqueia Done.
- Docs + kaizen-log.

**Non-Goals:**
- Forçar o DEV a abrir o protótipo no apply (#530).
- Check de rota nova (#529).

## Decisions

1. **Verify heurístico, fail-closed no óbvio.** Procurar no diff os arquivos/controles citados na task; ausência = CRITICAL.
2. **QA `[ ]` = blocker**, inclusive 7.x Playwright.
3. **UI impact: none.**

## UI impact

`none` — processo de verify/review.

## Prototype

N/A. Justificativa: sem tela nova; Alan valida a skill/docs.

## Impeccable Brief

N/A — `UI impact: none`.

## Impeccable Critique

N/A — `UI impact: none`.

## Impeccable Audit

N/A — `UI impact: none`.

## Impeccable Trace

N/A — `UI impact: none`.

## Risks / Trade-offs

- [Falsos positivos se a task for vaga] → Tasks de UI devem citar controle/estado; verify marca WARNING se a task não for auditável, CRITICAL se `[x]` e o texto aponta UI ausente.
- [Custo de review] → Checklist curta; não substitui Playwright (#529).

## Migration Plan

1. Aprovação de Design.
2. Atualizar verify skill, AGENTS, rules, kaizen-log.
3. QA visual inalterada.

## Open Questions

Nenhuma.

## Design Critique

- Escopo: verify/review exigem evidência de task de UI × protótipo.
- Crítica isolada: PASS. Sem UI de produto neste card.
- Superfície visual nova: nenhuma.

## Prototype Validation

N/A — sem protótipo navegável.

Design Agent verdict: PASS
