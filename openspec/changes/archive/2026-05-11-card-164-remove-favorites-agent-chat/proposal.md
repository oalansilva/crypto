## Why

Alan pediu simplificar a tela de Favoritos removendo a ação "Chat com agente". A tela deve continuar focada em curadoria, ranking e análise de estratégias, sem oferecer o chat nessa superfície.

## What Changes

- Remover da tela `/favorites` os botões/ações de chat com agente no layout desktop e mobile.
- Remover estado e modal de chat específicos de `FavoritesDashboard`, quando não forem mais usados.
- Preservar ações existentes de Favoritos: análise, exclusão administrativa, seleção, filtros e ranking por estrelas.
- Atualizar cobertura E2E para garantir que a tela não exibe "Chat com agente" nem ação "Trader" associada ao chat.

## Capabilities

### New Capabilities

### Modified Capabilities
- `favorites`: a tela de Favoritos não deve expor ação de chat com agente.

## Impact

- Frontend: `frontend/src/pages/FavoritesDashboard.tsx`.
- Testes: `frontend/tests/e2e/favorites-view-results.spec.ts`.
- Sem alteração de API, banco, permissões ou chat fora da tela de Favoritos.
