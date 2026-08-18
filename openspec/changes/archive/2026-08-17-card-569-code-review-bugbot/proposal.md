## Why

O gate `Status=Code Review` já existe e corre antes do commit, mas o agente ainda usa um `Task` genérico, sem prompt versionado nem comparação explícita com `develop`. O plano anterior tornava `/review-bugbot` obrigatório; Alan recusou ligar o produto Bugbot por custo (usage-based por PR/push). Sem pivot, o card ou cobra review pago, ou volta ao `Task` vago.

## What Changes

- Em `Status=Code Review`, o agente **sempre** dispara dois `Task` `generalPurpose` read-only com `model: inherit`:
  1. `.cursor/agents/diff-reviewer.md` — bugs/segurança/regressão no diff.
  2. `.cursor/agents/code-reviewer.md` — processo/OpenSpec/Design/não regressão de status.
- Pré-commit: diff não commitado vs HEAD. Fechamento: `origin/develop...HEAD` **ainda na branch do card** (nunca depois do squash em `develop`).
- `/review-bugbot` e `/review-security` ficam **opcionais**, só se Alan pedir no card. Bugbot de dashboard permanece Off de propósito (custo).
- Manter `.cursor/BUGBOT.md` (raiz + aninhados) como regras versionadas que o reviewer local lê (e o Bugbot leria se um dia ligasse).
- Autofix / Agent Review automático pós-commit permanecem desligados.
- Comentário de Done cita os dois reviewers locais, não Bugbot obrigatório.
- **Não é BREAKING** para produto/API/UI. É mudança de contrato operacional do harness.

## Capabilities

### New Capabilities

- `cursor-code-review`: gate de Code Review no Cursor com dois reviewers versionados `inherit`/`readonly` (diff vs HEAD no pré-commit; `origin/develop...HEAD` no fechamento) e Bugbot/Security Review opcionais.

### Modified Capabilities

- `cursor-harness`: o Code Review deixa de ser `Task` genérico; o caminho feliz usa prompts versionados no mesmo modelo do chat. Produtos gerenciados do Cursor não são o default.
- `delivery-qa-stage`: evidência de Code Review inclui os dois reviewers locais; Bugbot no PR não é gate.
- `developer-tooling`: versionar `.cursor/agents/diff-reviewer.md`, `.cursor/agents/code-reviewer.md` e `.cursor/BUGBOT.md` (regras compartilhadas).

## Impact

- Docs/contrato: `AGENTS.md`, `rules.md`, `docs/backlog-operating-model.md`, comentário canônico de Done, `docs/kaizen-log.md`, `docs/decision-log.md`.
- Tooling: `.cursor/agents/diff-reviewer.md`, `.cursor/agents/code-reviewer.md`, `.cursor/BUGBOT.md` + aninhados.
- Runtime de produto (API, UI, banco): nenhum.
- Automations/Bugbot no dashboard Cursor permanece Off; não é blocker.
