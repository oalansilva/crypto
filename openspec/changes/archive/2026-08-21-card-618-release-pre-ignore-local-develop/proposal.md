# Proposal: card-618-release-pre-ignore-local-develop

## Why

No closeout 2026-08-19, `release-guard pre` com `HEAD=release-*` emitiu BLOCKER `local branch not merged: develop` porque a ref local `develop` estava ahead de `origin/develop` (arquivo/archive não publicado). O operador desbloqueou com `git branch -f develop origin/develop`. Kaizen F-3: decisões de release já usam `origin/develop`; forçar alinhamento da ref local (ou `PRESERVED_BRANCHES=develop`) queima o turno de closeout sem ganho de segurança.

## What Changes

- Em `mode=pre` com branch atual `release-*`, a seção **Local branches** deixa de tratar `develop` local como branch extra não mergeada (skip / não-blocker), **sem** exigir `PRESERVED_BRANCHES=develop`.
- O aviso já existente quando `refs/heads/develop` ≠ `origin/develop` permanece (release decisions use `origin/develop`).
- Fixture/teste cobre o caso: `pre` em `release-*` + `develop` local ahead de `origin/develop` ⇒ sem BLOCKER de local branch para `develop`.
- Sem mudança de UI, produto, board ou playbook de deploy.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `release-worktree-hygiene`: em `pre` com `HEAD=release-*`, ignorar (não bloquear) a ref local `develop` no inventário de local branches não mergeadas; não exigir `PRESERVED_BRANCHES=develop`.

## Impact

- `scripts/release-guard` — seção Local branches (~1120–1140) e interação com o warn de develop ≠ origin (~438–447).
- `backend/tests/integration/test_release_guard.py` — novo caso de fixture.
- Overlay/AGENTS: sem obrigatoriedade de documentar `PRESERVED_BRANCHES=develop` para este cenário.
- **Não** altera `post`/`audit`, GraphQL budget, nem classificação de card branches in-flight via `PRESERVED_BRANCHES`.
