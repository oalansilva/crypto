# Proposal: card-581-release-guard-preserve

## Why

O `pre` da release 2026-08-17 lote 2 falhou por worktrees extras (cards já mergeados + #569 in-flight) e depois por `card-569-code-review-bugbot` local não mergeada. O WIP do #569 precisou de commit de preservação e delete da ref local, embora o remoto tenha sido classificado via `PRESERVED_BRANCHES` só no `post`/`audit`. Contornável, mas queima o turno de closeout.

## What Changes

- `pre` aceita worktree/branch local **classificada** em `PRESERVED_BRANCHES` (card em Design / Aprovação de Design / demais não terminais) em vez de blocker genérico “extra worktree”.
- Worktree de branch **já em `origin/develop`** cujo único delta sujo é `docs/release-${RELEASE_DATE}.md` não é dirty blocker; closeout pode remover a worktree sem commit vazio. A seção **Local branches** do `pre` também respeita `PRESERVED_BRANCHES`.
- `pre` MUST NOT carregar snapshot do Project (orçamento GraphQL existente: zero `item-list` em `pre`). Classificação in-flight = `PRESERVED_BRANCHES`, não lookup de Status.

## UI impact

`none`

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `release-worktree-hygiene`: classificação de preserve também no `pre`; dirty de rollout PROD em branch mergeada deixa de ser blocker.

## Impact

`scripts/release-guard` seção Worktrees; `AGENTS.md` (como exportar `PRESERVED_BRANCHES` no `pre`). WIP já presente na worktree deste card é rascunho **inválido** (chama board em `pre`) e MUST ser reescrito no apply.
