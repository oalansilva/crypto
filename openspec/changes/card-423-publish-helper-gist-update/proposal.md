## Why

Cada republicação de artefatos OpenSpec cria novo Gist (F-3: #361 com 3 Gists, #399 com 3 Gists) e novo comentário quase idêntico no card, gerando sprawl e ruído; e ajustes pós-review commitados um a um produzem PRs fragmentados + commit vazio de retrigger de CI (F-4).

## What Changes

- `publish-openspec-card-artifacts.sh` aceitar `--gist-id <id>` e atualizar o Gist existente (criar só na primeira publicação); manter instrução no AGENTS.md.
- Documentar/scriptar retrigger de CI via `workflow_dispatch` (`gh workflow run`) em vez de commit vazio.
- Orientação de agrupar ajustes pós-review em um único commit/PR (docs/fluxo).

## Capabilities

### New Capabilities

- `gist-update-republication`: atualização de Gist existente por `--gist-id` sem criar Gists duplicados por change.

### Modified Capabilities

- `developer-tooling`: o helper de publicação de artefatos OpenSpec passa a atualizar Gist existente e o retrigger de CI usa `workflow_dispatch` sem commit vazio.

## Impact

- Helper `publish-openspec-card-artifacts.sh` (skill alan-workflow).
- Documentação/fluxo em `AGENTS.md` (comando de retrigger e agrupamento de ajustes pós-review).
- Sem mudanças de runtime, banco ou frontend.
