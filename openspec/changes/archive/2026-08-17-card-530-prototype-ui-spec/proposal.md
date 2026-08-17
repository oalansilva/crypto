## Why

No #469 o DEV implementou a UI pelo contrato de API (preflight, lifecycle, tabela) sem abrir o protótipo aprovado. `DiscoveryPage.tsx` saiu sem busca/checkbox de catálogo, card de preflight, progress bar, filtros/paginação, modal de promoção e estados críticos. O fluxo atual não obriga nem registra o passo de carregar o protótipo como spec de UI.

## What Changes

- `/opsx:apply` com `UI impact: affected` exige carregar `design.md` + protótipo aprovado (`frontend/public/prototypes/<change>/`) como spec de UI antes de codar.
- Contrato de API é fonte de integração/dados, não de layout.
- Handoff/PR registra que o protótipo foi consultado e quais elementos foram seguidos; ausência é blocker de apply.
- Desvios vs protótipo são justificados e explícitos (nunca silenciosos).
- Antes de Code Review, o DEV compara rota entregue vs protótipo e registra o resultado.
- Atualizar `AGENTS.md`/`rules.md` e registrar exemplo no `docs/kaizen-log.md`.
- Dependências de processo: #529 (CI da superfície) e #531 (evidência por task). Este card ataca a causa comportamental no apply.

## Capabilities

### New Capabilities

- `prototype-as-ui-spec`: protótipo aprovado é a spec de layout no apply quando `UI impact: affected`.

### Modified Capabilities

- `design-approval-evidence`: apply/handoff passam a exigir consulta registrada ao protótipo.
- `developer-tooling`: skill `/opsx:apply` inclui o passo obrigatório de carregar o protótipo.

## Impact

- `.cursor/skills/openspec-apply-change/SKILL.md`, `AGENTS.md`, `rules.md`, `.agents/skills/design-critic/SKILL.md` se necessário.
- `docs/kaizen-log.md` (exemplo #469).
- Sem mudança de UI de produto neste card.
