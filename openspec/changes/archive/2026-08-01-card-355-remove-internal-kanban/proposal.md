## Why

A página interna `/kanban` cria um board paralelo ao GitHub Project oficial (`https://github.com/users/oalansilva/projects/1/views/1`). Alan opera só o Project 1; manter a UI interna gera confusão operacional e esforço de processo no app errado.

## What Changes

- **BREAKING (UI):** remover a rota SPA `/kanban` e a página `KanbanPage` do produto autenticado.
- Remover layout especial wide-shell exclusivo do Kanban e qualquer deep-link/navegação residual para `/kanban`.
- Remover/ajustar testes E2E e snapshots visuais que exercitam a tela `/kanban`.
- Atualizar specs/docs/processo para declarar o GitHub Project 1 como único board operacional; `/kanban` deixa de ser superfície de produto.
- **Decisão de API:** manter `/api/workflow/kanban/*` neste card — ainda alimentam Home (snapshot de changes) e automação/agents; sem UI de board. Remoção/renomeação dessas APIs fica fora de escopo (card futuro se Alan pedir).

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `kanban`: remover requisitos de UI board em `/kanban`; board operacional oficial passa a ser o GitHub Project 1; APIs workflow/kanban permanecem como contrato de dados/automação sem superfície de board no app.
- `mobile-kanban-ui`: descontinuar requisitos da UI mobile do Kanban interno (página removida).

## Impact

- Frontend: `App.tsx`, `KanbanPage.tsx`, `Layout.tsx`, CSS `.kanban-page`, E2E `kanban-*.spec.ts`, snapshots `kanban-*` em `visual-critical`.
- Backend: sem remoção de rotas neste card; apenas documentação da decisão.
- Processo: `AGENTS.md`/`rules.md`/`docs/*` alinhados ao Project 1 (já parcialmente alinhados; corrigir qualquer menção residual a `/kanban` como board).
- Fora: card #353 (Admin Backfill); campos/colunas do GitHub Project 1.
