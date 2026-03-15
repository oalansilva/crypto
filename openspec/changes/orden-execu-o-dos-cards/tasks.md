# Tasks — orden-execu-o-dos-cards

## 1. Runtime / Backend
- [x] 1.1 Definir o modelo de persistência da ordem de cards dentro da mesma coluna/etapa.
- [x] 1.2 Implementar endpoint/ação de reorder usado pelo Kanban.
- [x] 1.3 Garantir leitura estável da ordem nas consultas do board.
- [x] 1.4 Validar que a operação não permite burlar gates nem mover cards entre colunas fora do fluxo.

## 2. Frontend Kanban UX
- [x] 2.1 Definir affordance de reorder no board/detalhe para mover card para cima/baixo.
- [x] 2.2 Atualizar a UI para refletir a nova ordem sem reload manual.
- [x] 2.3 Tratar estados de erro/conflito quando a persistência falhar.
- [x] 2.4 Garantir um comportamento utilizável também no mobile, mesmo que com interação diferente do desktop.

## 3. Validation / Tests
- [x] 3.1 Cobrir persistência de reorder com testes backend.
- [x] 3.2 Cobrir leitura ordenada do board com testes backend/integration.
- [x] 3.3 Adicionar cobertura frontend/E2E para reorder bem-sucedido.
- [x] 3.4 Adicionar cobertura para refresh/reload preservando a ordem salva.

## 4. Documentation / Handoff
- [x] 4.1 Atualizar documentação/specs do Kanban e workflow-state-db para a nova fila ordenada.
- [x] 4.2 Registrar a convenção operacional de pull-order pelos agentes.
- [x] 4.3 Reconciliar runtime/Kanban + handoff no fim de cada stage.
