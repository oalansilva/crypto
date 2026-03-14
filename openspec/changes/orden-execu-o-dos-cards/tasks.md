# Tasks — orden-execu-o-dos-cards

## 1. Runtime / Backend
- [ ] 1.1 Definir o modelo de persistência da ordem de cards dentro da mesma coluna/etapa.
- [ ] 1.2 Implementar endpoint/ação de reorder usado pelo Kanban.
- [ ] 1.3 Garantir leitura estável da ordem nas consultas do board.
- [ ] 1.4 Validar que a operação não permite burlar gates nem mover cards entre colunas fora do fluxo.

## 2. Frontend Kanban UX
- [ ] 2.1 Definir affordance de reorder no board/detalhe para mover card para cima/baixo.
- [ ] 2.2 Atualizar a UI para refletir a nova ordem sem reload manual.
- [ ] 2.3 Tratar estados de erro/conflito quando a persistência falhar.
- [ ] 2.4 Garantir um comportamento utilizável também no mobile, mesmo que com interação diferente do desktop.

## 3. Validation / Tests
- [ ] 3.1 Cobrir persistência de reorder com testes backend.
- [ ] 3.2 Cobrir leitura ordenada do board com testes backend/integration.
- [ ] 3.3 Adicionar cobertura frontend/E2E para reorder bem-sucedido.
- [ ] 3.4 Adicionar cobertura para refresh/reload preservando a ordem salva.

## 4. Documentation / Handoff
- [ ] 4.1 Atualizar documentação/specs do Kanban e workflow-state-db para a nova fila ordenada.
- [ ] 4.2 Registrar a convenção operacional de pull-order pelos agentes.
- [ ] 4.3 Reconciliar runtime/Kanban + handoff no fim de cada stage.
