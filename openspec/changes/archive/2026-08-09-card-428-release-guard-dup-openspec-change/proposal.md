## Why

O archive da change `card-420-kaizen-agent` foi feito na branch de release (main-side) e o sync back para `develop` adicionou o archive sem remover a pasta ativa, deixando a change ativa e arquivada ao mesmo tempo (F-1 da auditoria 2026-08-09). Foi corrigido manualmente (PR #427), mas sem automação o padrão pode recorrer em todo sync de release.

## What Changes

- `scripts/release-guard post`: verificar que nenhuma change ativa em `openspec/changes/` tem correspondente em `openspec/changes/archive/*/`; falhar/diagnosticar quando houver duplicação após sync.
- Aplicar o mesmo check no fluxo de sync `main -> develop` (passo pós-publicação).

## Capabilities

### New Capabilities

- `duplicate-openspec-change-detection`: detecção de change OpenSpec duplicada (ativa + arquivada) com blocker e instrução de correção.

### Modified Capabilities

- `release-worktree-hygiene`: o guard pós-release valida a não duplicação de changes OpenSpec após sync `main -> develop`.

## Impact

- `scripts/release-guard` (modo `post`).
- `AGENTS.md`/docs do fluxo de sync.
- Sem mudanças de runtime, banco ou frontend.
