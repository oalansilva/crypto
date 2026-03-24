## 1. Remoção da superfície de UI

- [ ] 1.1 Remover `/arbitrage` de `frontend/src/App.tsx` e excluir a página `frontend/src/pages/ArbitragePage.tsx`
- [ ] 1.2 Remover item, ícone e resolução de título de arbitragem em `frontend/src/components/AppNav.tsx`
- [ ] 1.3 Revisar cópias, atalhos e protótipos vivos para eliminar referências ativas à funcionalidade

## 2. Limpeza do backend de arbitragem

- [ ] 2.1 Remover o endpoint `/api/arbitrage/spreads` de `backend/app/api.py`
- [ ] 2.2 Remover monitor assíncrono, estado de app e flag `arbitrage_monitor_enabled` do ciclo de vida/configuração do backend
- [ ] 2.3 Excluir serviços e logs dedicados à arbitragem se não houver mais consumidores após a busca global

## 3. Testes e documentação operacional

- [ ] 3.1 Remover ou atualizar testes dedicados à arbitragem em `tests/` e fixtures relacionadas
- [ ] 3.2 Atualizar `docs/qa-ui-checklist.md` e demais referências operacionais vivas para não listar Arbitrage como fluxo obrigatório
- [ ] 3.3 Rodar busca final por `arbitrage|arbitragem` fora de arquivos arquivados e reconciliar sobras intencionais

## 4. Validação

- [ ] 4.1 Validar que a navegação não expõe mais arbitragem e que `/arbitrage` não possui rota ativa
- [ ] 4.2 Validar que `/api/arbitrage/spreads` responde como recurso inexistente e que o backend não inicia monitor dedicado
- [ ] 4.3 Executar checks direcionados de frontend/backend afetados por esta remoção
- [ ] 4.4 Quando aplicável, usar skills em `.codex/skills` para frontend, debugging e tests durante a implementação e QA
