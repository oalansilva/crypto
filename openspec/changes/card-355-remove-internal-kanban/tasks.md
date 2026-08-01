## 1. Frontend — remover UI `/kanban`

- [x] 1.1 Remover `KanbanPage` e imports associados
- [x] 1.2 Substituir rota `/kanban` por redirect para `/monitor` (sem renderizar o board)
- [x] 1.3 Remover wide-shell/`isKanbanRoute` em `Layout.tsx` se ficar morto
- [x] 1.4 Limpar CSS `.kanban-page` morto proporcional ao diff

## 2. Testes e QA visual

- [x] 2.1 Remover ou reescrever E2E `kanban-*.spec.ts` que dependem da página
- [x] 2.2 Remover cenários/snapshots `kanban-*` de `visual-critical.spec.ts`
- [x] 2.3 Manter mocks de `/api/workflow/kanban/changes` só onde Home/outros testes ainda precisam
- [x] 2.4 Atualizar/remover `qa_screenshot_kanban_mobile.mjs` se referenciar a rota removida

## 3. Docs e processo

- [x] 3.1 Garantir que `AGENTS.md`/`rules.md`/`docs/*` não apontem `/kanban` como board operacional
- [x] 3.2 Registrar decisão: APIs `/api/workflow/kanban/*` mantidas neste card

## 4. Backend (sem remoção neste card)

- [x] 4.1 Confirmar que rotas `/api/workflow/kanban/*` permanecem intactas (smoke/leitura)
- [x] 4.2 Não alterar workflow DB / stage gates neste card

## 5. Verificação

- [x] 5.1 `openspec validate card-355-remove-internal-kanban` (ou equivalente da change)
- [x] 5.2 Testes focados frontend/E2E afetados verdes
- [ ] 5.3 Após integração em `develop`: `./restart` e validar que `/kanban` não mostra o board
