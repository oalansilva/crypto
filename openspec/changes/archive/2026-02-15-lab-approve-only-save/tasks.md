# Tasks

## 1. Identificar pontos de salvamento automático
- [ ] 1.1 Localizar todos os pontos onde templates são salvos em `combo_templates` durante fluxo do Lab
- [ ] 1.2 Mapear arquivos: `backend/app/lab/*.py`, `backend/app/routers/lab.py`
- [ ] 1.3 Documentar funções que fazem salvamento automático

## 2. Modificar fluxo de geração de candidatos
- [ ] 2.1 Remover salvamento automático em `combo_templates` durante geração de candidato
- [ ] 2.2 Manter dados apenas no contexto da run (memória/log)
- [ ] 2.3 Garantir que candidatos são acessíveis para o Trader review sem estar no banco

## 3. Criar API de aprovação do Trader
- [ ] 3.1 Criar endpoint `POST /lab/{run_id}/approve`
- [ ] 3.2 Recuperar dados da run (template_data, description)
- [ ] 3.3 Criar template em `combo_templates` com nome apropriado
- [ ] 3.4 Marcar run como `approved`
- [ ] 3.5 Retornar nome do template criado

## 4. Modificar API de rejeição
- [ ] 4.1 Criar/modificar endpoint `POST /lab/{run_id}/reject`
- [ ] 4.2 APENAS marcar run como `rejected`
- [ ] 4.3 Garantir que NENHUM template é criado em `combo_templates`

## 5. Ajustar UI de review do Trader
- [ ] 5.1 Garantir que botão "Aprovar" chama API de aprovação
- [ ] 5.2 Garantir que botão "Rejeitar" chama API de rejeição
- [ ] 5.3 Adicionar feedback visual (toast/alert) de sucesso/erro

## 6. Testes
- [ ] 6.1 Testar fluxo aprovação: Dev → Candidato → Trader Aprova → Template existe no banco
- [ ] 6.2 Testar fluxo rejeição: Dev → Candidato → Trader Rejeita → Template NÃO existe
- [ ] 6.3 Verificar que `/combo/select` só mostra templates aprovados
- [ ] 6.4 Rodar `pytest` para validar backend
