## Why

O #609 versionou a tabela, mas o Agent ainda classifica o card pelo cwd da sessão. Write num path de outra branch/`develop` passa despercebido. O lote 1 precisa do resolver `(q, bound_card, q_git)` antes do Guard (#611).

## What Changes

- Adicionar em `scripts/process-fsm/` um resolver que, dado cwd + path do arquivo + `#id` opcional, devolve `(q, bound_card, q_git)` usando `.cursor/process-fsm.yaml` já em `develop`.
- Classificar `q_git` pelo worktree **do path**, não pelo cwd.
- Ambíguo ou sem card ⇒ `bound_card=⊥`.
- Fixtures sem GitHub/hook: cwd≠path, `develop`/`main`, unbound.
- Não ligar `preToolUse` (#611). Não alterar produto.

## Capabilities

### New Capabilities

- `process-fsm-resolver`: resolução de `(q, bound_card, q_git)` a partir de filesystem/git.

### Modified Capabilities

- (nenhuma) — `process-fsm` do #609 é lido, não alterado.

## Impact

- `scripts/process-fsm/` (novo módulo + testes). Yaml do #609 não muda a matriz.
- Sem API, UI, hook Cursor.
- `UI impact: none`. Prototype N/A.
