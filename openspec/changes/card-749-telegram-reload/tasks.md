## 1. Frontend — correção 401 transitório (defense in depth)

- [x] 1.1 Reforçar `authFetch` (`frontend/src/lib/authFetch.ts:142`) para que retry com `refreshAuthToken()` bem-sucedido retorne 200 ao caller e só retorne 401 original quando `refreshToken` ausente/falha com `notifyAuthSessionCleared` (`missing-refresh-token`/`refresh-failed`/`refresh-invalid`/`refresh-error`).
- [x] 1.2 Em `TelegramAlertsForm.tsx:36-46` preservar `settings` stale no `catch` quando já houve 200 válido (guard `prevSettingsRef`/`settings !== null`): só `setSettings(null)` se primeira carga nunca sucedeu; manter `loading` até retry final; toast apenas em 401 real ou se nunca houve 200.
- [x] 1.3 Adicionar `AbortController`/flag `cancelled` no `useEffect(()=>void loadSettings(),[loadSettings])` e checar antes de `setSettings`/`setLoading`/`onSettingsChange`; passar `signal` para `authFetch` se suportado.
- [x] 1.4 Estabilizar deps `useCallback` em `TelegramAlertsForm.tsx:56`: guardar `onSettingsChange` via `useRef` (atualizar em `useEffect`) ou memoizar no pai; usar `toast` global estável em vez de objeto `useToast()` recriado.

## 2. Frontend — sync Monitor + guard opcional

- [x] 2.1 Aplicar mesma lógica de não zerar em 401 transitório em `MonitorStatusTab.tsx:395` (`fetchMonitorContext`): preservar `telegramAlertsEnabled` anterior em catch quando já houve valor; adicionar `cancelled`/`Abort` no `useEffect` que chama `fetchMonitorContext`.
- [x] 2.2 Avaliar guard `isLoading` em `ProfilePage.tsx:208` (`useAuth().isLoading`) — só invocar/mostrar `TelegramAlertsForm` quando `isLoading===false` para reduzir corrida com `AuthProvider` verify (`authStore.tsx:126`); documentar se não bloqueante.

## 3. Testes — travar regressão (criteria 6)

- [x] 3.1 Unit `frontend/src/components/telegram/TelegramAlertsForm.test.tsx`: mockar `authFetch` sequenciando 401 → `POST /auth/refresh` 200 → retry 200 com `linked:true` e validar que `Status: Vinculado` permanece; segundo caso 401 real (refresh falha) valida `setSettings(null)`/logout não mascarado.
- [x] 3.2 E2E Playwright `frontend/tests/e2e/telegram-reload.spec.ts` (ou extensão de `visual-critical.spec.ts`): mock `GET /api/users/me/telegram-settings` com `{ linked:true, linkedAt:'2026-08-27T00:50:58Z', botUsername:'Criptofarol_bot', telegramAlertsEnabled:true }` + `GET /api/users/me`; `page.goto('/profile')` e `page.reload()` → `expect(getByTestId('telegram-alerts-form'))` contém `Vinculado`, `Vinculado em`, `Bot: @Criptofarol_bot` e `telegram-alerts-enabled` checked.
- [x] 3.3 Validar sync Monitor: e2e ou unit verifica que `PATCH /users/me/telegram-settings` de `TelegramAlertsForm` e `MonitorStatusTab` (`data-testid="monitor-telegram-alerts-toggle"`) refletem mesmo `telegramAlertsEnabled` após reload em ambas as páginas.

## 4. Validação & publicação Design

- [ ] 4.1 `openspec validate --change card-749-telegram-reload` e `openspec validate --all` (ou validação parcial do spec afetado) verdes; `npm run lint`/`tsc` sem erros no frontend.
- [ ] 4.2 Publicar artefatos no card: `publish-openspec-card-artifacts.sh --repo oalansilva/crypto --issue 749 --change card-749-telegram-reload` (Gist `crypto openspec card-749-telegram-reload` + comentário) sem HTML no Gist; `design.md` já contém `Impeccable N/A` justificado e `Design Critique` PASS; `UI impact: none` com `Prototype N/A`.
- [ ] 4.3 Recriticar se necessário e submeter: `python3 scripts/process-fsm/process_event.py submeter_design --card 749` (T5) → `Aprovação de Design` aguardando T7 Alan.
