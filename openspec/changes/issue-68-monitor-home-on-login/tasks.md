# Tasks: Monitor as Post-Login Home

- [x] [1] Atualizar `frontend/src/pages/LoginPage.tsx` para redirecionar para `/monitor` após login/cadastro.
- [x] [2] Atualizar `frontend/src/App.tsx` para tornar `/` (index autenticado) um redirecionamento para `/monitor` e preservar `HomePage` em `/home`.
- [x] [3] Ajustar fallback de autenticação em `frontend/src/components/ProtectedLayout.tsx` e `frontend/src/components/ProtectedRoute.tsx` para preservar retorno da rota original no `login`.
- [x] [4] Ajustar navegação principal (`frontend/src/components/AppNav.tsx`) para evitar referência a `/` como “Playground”.
- [x] [5] Atualizar teste E2E `frontend/tests/e2e/homepage-real-data.spec.ts` para consumir `/home` explicitamente.
- [x] [6] Criar `frontend/tests/e2e/issue-68-monitor-home.spec.ts` cobrindo `/ -> /monitor` e login -> `/monitor`.
- [x] [7] Registrar a mudança em `openspec/changes/issue-68-monitor-home-on-login/` com proposta, especificação e rastreio de tarefas.
