# Tasks — alterar-dados-dos-cards

## 1. Runtime / Backend
- [ ] 1.1 Definir o comportamento runtime para edição de `title` e `description` de changes/cards existentes.
- [ ] 1.2 Implementar endpoint/path de update usado pelo Kanban para salvar título e descrição.
- [ ] 1.3 Definir e implementar o comportamento de cancelamento sem exclusão física do card.
- [ ] 1.4 Garantir que comments/handoff e consultas do board continuem coerentes após edição/cancelamento.

## 2. Frontend Kanban UX
- [x] 2.1 Adicionar affordance de editar card no detalhe/drawer do Kanban.
- [x] 2.2 Permitir editar título e descrição com validação básica e feedback de erro.
- [x] 2.3 Adicionar ação de cancelamento com confirmação explícita.
- [x] 2.4 Atualizar board/detalhe automaticamente após salvar ou cancelar.

## 3. Validation / Tests
- [ ] 3.1 Cobrir update de título/descrição com testes backend.
- [ ] 3.2 Cobrir cancelamento com testes backend, incluindo preservação de histórico e comportamento esperado no runtime.
- [x] 3.3 Adicionar cobertura frontend/E2E para editar um card existente.
- [x] 3.4 Adicionar cobertura frontend/E2E para cancelar um card existente.

## 4. Documentation / Handoff
- [ ] 4.1 Atualizar a documentação/specs do Kanban e workflow-state-db para o novo fluxo.
- [ ] 4.2 Preparar review PT-BR com a decisão funcional de "cancelar sem deletar".
- [ ] 4.3 Reconciliar runtime/Kanban + handoff no fim de cada stage.
