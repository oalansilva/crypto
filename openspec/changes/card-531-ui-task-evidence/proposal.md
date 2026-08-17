## Why

No #469 o `tasks.md` marcou 6.2–6.10 como `[x]` sem código correspondente e deixou 7.8/7.9 (Playwright) em `[ ]`. `/opsx:verify` e Code Review não confrontaram a checklist com a implementação nem com o protótipo. O card fechou Done. A checklist é autodeclaração.

## What Changes

- Task de UI só fecha `[x]` com evidência verificável (arquivo, commit ou spec).
- Code Review inclui checklist “UI tasks: implementadas e verificadas contra protótipo”; `[x]` sem implementação é blocker de review.
- `/opsx:verify` ganha item obrigatório para `UI impact: affected`: superfície vs protótipo, resultado no handoff antes de Done.
- Toda task de testes (frontend/Playwright) precisa estar `[x]` com evidência antes de Done; `[ ]` em QA é blocker.
- Atualizar `AGENTS.md`/`rules.md` e exemplo no `docs/kaizen-log.md`.
- Dependências: #529 (CI) e #530 (protótipo como spec no apply). Este card fecha o verify/review.

## Capabilities

### New Capabilities

- `ui-task-evidence`: tasks de UI e de teste só contam como feitas com evidência cruzada (código × protótipo × spec).

### Modified Capabilities

- `card-close-evidence-integrity`: Done bloqueado se task de QA estiver `[ ]` ou task de UI `[x]` sem evidência.
- `design-approval-evidence`: verify/review comparam entrega vs protótipo aprovado.

## Impact

- `.cursor/skills/openspec-verify-change/SKILL.md`, `AGENTS.md`, `rules.md`.
- `docs/kaizen-log.md`.
- Sem mudança de UI de produto neste card.
