## Why

O guard automatizado não detecta cards em `Pronto` sem deploy em PROD (F-7: release fechada com cards `Pronto` sem deploy, corrigida só manualmente) nem inventaria refs/worktrees órfãs que permanecem sem classificação após releases (F-5: `runtime-*`, `rollback-*`, `release-post-*`, `preserve/*` com WIP não commitado).

## What Changes

- `release-guard pre`: adicionar check de evidência de deploy PROD (commit publicado no source PROD, services reiniciados, URL pública validada) antes de liberar `Pronto`.
- `release-guard post`: inventariar refs `runtime-*`/`rollback-*`/`release-post-*`/`sync-*` e worktrees `preserve/*`, exigindo classificação (integrar/preservar/limpar com autorização) e sinalizando WIP não commitado.
- Atualizar docs/AGENTS para refletir o novo comportamento.

## Capabilities

### New Capabilities

- `prod-deploy-evidence-check`: verificação automatizada de evidência de deploy PROD antes de mover cards para `Pronto`.
- `orphan-ref-inventory`: inventário de refs/worktrees órfãs no modo `post` com exigência de classificação.

### Modified Capabilities

- `release-worktree-hygiene`: o guard de release passa a validar evidência de deploy PROD e a inventariar refs/worktrees órfãs e WIP não commitado.

## Impact

- `scripts/release-guard` (modos `pre` e `post`).
- `AGENTS.md`/`rules.md` e skill `alan-workflow-ambientes` conforme necessário.
- Sem mudanças de runtime, banco ou frontend.
