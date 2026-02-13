# Tasks: Lab - Persistência Condicional de Templates

## Task 1: Identificar pontos de salvamento automático
**Arquivos**: `backend/app/lab/*.py`, `backend/app/routers/lab.py`
**Descrição**: Encontrar todos os locais onde templates são salvos em `combo_templates` durante o fluxo do Lab.

## Task 2: Modificar fluxo de geração de candidatos
**Arquivos**: Backend Lab
**Descrição**: 
- Remover salvamento automático em `combo_templates`
- Manter dados apenas no contexto da run (memória/log)
- Garantir que candidatos são acessíveis para o Trader review

## Task 3: Criar/Modificar API de aprovação
**Arquivos**: `backend/app/routers/lab.py` ou similar
**Descrição**:
- Endpoint `POST /lab/{run_id}/approve`
- Recuperar dados da run
- Criar template em `combo_templates` com nome apropriado
- Marcar run como aprovada
- Retornar nome do template criado

## Task 4: Modificar API de rejeição
**Arquivos**: `backend/app/routers/lab.py` ou similar
**Descrição**:
- Endpoint `POST /lab/{run_id}/reject`
- APENAS marcar run como rejeitada
- Garantir que NENHUM template é criado
- Opcional: feedback ao Dev

## Task 5: Verificar UI de review do Trader
**Arquivos**: `frontend/src/pages/Lab*.tsx`
**Descrição**:
- Garantir que botão "Aprovar" chama API de aprovação
- Garantir que botão "Rejeitar" chama API de rejeição
- Adicionar feedback visual de sucesso/erro

## Task 6: Testes
**Descrição**:
- Testar fluxo completo: Dev → Candidato → Trader Aprova → Template existe
- Testar rejeição: Dev → Candidato → Trader Rejeita → Template NÃO existe
- Verificar que `/combo/select` só mostra templates aprovados

## Task 7: Cleanup (opcional)
**Descrição**: Remover templates "lab_" antigos se ainda existirem (já feito anteriormente).
