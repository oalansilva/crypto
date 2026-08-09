## Why

O fechamento da release 2026-08-09 revelou evidência documental do deploy PROD apenas no worktree (doc com placeholders em develop/main; dois docs de release da mesma data em paralelo) e cards do pacote com campos do board vazios (#413/#416 sem Responsável/Prioridade; #416 título divergente).

## What Changes

- `release-guard post`: falhar se a doc do pacote tiver placeholders ou não estiver commitada; falhar se houver 2+ docs de release da mesma data com conteúdo divergente.
- `release-guard post`: falhar se card do pacote estiver sem Responsável/Prioridade/Tipo.
- Manter consistência título board/issue (vinculado a #430).

## Capabilities

### New Capabilities

- `documental-board-evidence-validation`: validação automatizada de evidência documental (doc commitada sem placeholders, única por data) e de campos do board (Responsável/Prioridade/Tipo) antes de `Pronto`.

### Modified Capabilities

- `release-worktree-hygiene`: o guard pós-release valida evidência documental e campos do board dos cards do pacote.

## Impact

- `scripts/release-guard` (modo `post`).
- `AGENTS.md`/docs de release.
- Sem mudanças de runtime, banco ou frontend.
