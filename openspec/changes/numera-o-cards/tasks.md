# Tasks — numera-o-cards

## 1. Runtime / Backend
- [ ] 1.1 Definir onde a numeração sequencial do card será persistida no runtime/workflow.
- [ ] 1.2 Garantir que cards existentes e novos recebam um número estável e não duplicado.
- [ ] 1.3 Expor o número nas consultas/endpoints usados pelo Kanban.
- [ ] 1.4 Garantir que reorder, mudança de coluna e edição do card não alterem a numeração já atribuída.

## 2. Frontend Kanban
- [ ] 2.1 Exibir a numeração no card de forma visível, sem poluir a leitura do título.
- [ ] 2.2 Exibir a mesma numeração no drawer/detalhe do card.
- [ ] 2.3 Garantir fallback consistente quando o board carregar cards antigos durante a migração.

## 3. Validation / Tests
- [ ] 3.1 Cobrir a geração/estabilidade da numeração com testes backend.
- [ ] 3.2 Cobrir o payload do board contendo o número esperado.
- [ ] 3.3 Validar no frontend/E2E que a numeração aparece e permanece estável após reload.

## 4. Documentation / Handoff
- [ ] 4.1 Atualizar a documentação/spec do Kanban com o identificador numérico humano.
- [ ] 4.2 Registrar na handoff comment a convenção de uso do número para referência operacional/QA.
