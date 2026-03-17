# Proposta: Cancelar card com reversão

## Problema

Atualmente, cards no Kanban podem ser **arquivados** (coluna "Archived"), mas não há como **reativá-los**. Uma vez arquivado, o card fica permanentemente fora do fluxo.

## Solução Proposta

Implementar funcionalidade de **reativação de cards arquivados**, permitindo que cards na coluna "Archived" sejam movidos de volta para uma coluna ativa (ex: "Pending").

### Escopo

1. **Backend (API)**
   - Criar endpoint para reativar card arquivado (`POST /api/workflow/changes/{change_id}/reactivate`)
   - O endpoint deve:
     - Mover o card de volta para "Pending"
     - Remover o card da pasta `archive` no filesystem
     - Atualizar o status no metadata do card

2. **Frontend (UI)**
   - Na visualização do card arquivado, substituir/substituir o botão "Já cancelado" por "Reativar card"
   - Ao reativar, mover o card de volta para "Pending"
   - Feedback visual de sucesso/erro

3. **Testes**
   - Teste de reativação via API
   - Teste E2E de reativação via UI

### Critérios de Aceitação

- [ ] Card arquivado pode ser reativado via UI
- [ ] Card reativado aparece na coluna "Pending"
- [ ] Card reativado é removido da pasta archive
- [ ] Feedback visual claro durante a reativação
- [ ] Testes passando

### Riscos

- Baixo risco: funcionalidade isolada, bem definida
- Manter backwards compatibility com cards já arquivados
