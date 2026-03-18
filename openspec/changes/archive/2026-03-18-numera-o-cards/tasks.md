# Tasks — numera-o-cards

## 1. Runtime / Backend
- [x] 1.1 Definir onde a numeração sequencial do card será persistida no runtime/workflow.
- [x] 1.2 Garantir que cards existentes e novos recebam um número estável e não duplicado.
- [x] 1.3 Expor o número nas consultas/endpoints usados pelo Kanban.
- [x] 1.4 Garantir que reorder, mudança de coluna e edição do card não alterem a numeração já atribuída.

## 2. Frontend Kanban
- [x] 2.1 Exibir a numeração no card de forma visível, sem poluir a leitura do título.
- [x] 2.2 Exibir a mesma numeração no drawer/detalhe do card.
- [x] 2.3 Garantir fallback consistente quando o board carregar cards antigos durante a migração.

## 3. Validation / Tests
- [x] 3.1 Cobrir a geração/estabilidade da numeração com testes backend.
- [x] 3.2 Cobrir o payload do board contendo o número esperado.
- [x] 3.3 Validar no frontend/E2E que a numeração aparece e permanece estável após reload.

## 4. Documentation / Handoff
- [x] 4.1 Atualizar a documentação/spec do Kanban com o identificador numérico humano.
- [x] 4.2 Registrar na handoff comment a convenção de uso do número para referência operacional/QA.
