## Why

Após homologação do #747 em DEV, o vínculo Telegram persiste no banco (`telegram_alerts_enabled=true`, `telegram_chat_id` preenchido, `telegram_linked_at` setado) mas o reload de `/profile` mostra `Status: Não vinculado` e toggle desligado até próxima interação (salvar/Gerar vínculo). Logs mostram `GET /api/users/me/telegram-settings` 200 e 401 no mesmo mount; `TelegramAlertsForm.tsx:46` faz `catch { setSettings(null) }` mascarando o 200 válido. É necessário corrigir a corrida sem mascarar logout real.

## What Changes

- Corrigir `frontend/src/components/telegram/TelegramAlertsForm.tsx` (Perfil) e `frontend/src/components/monitor/MonitorStatusTab.tsx` (Monitor, `fetchMonitorContext`/`toggleTelegramAlerts`) para não limpar UI útil em `401 transitório` quando `authFetch` fará retry com sucesso — defense in depth: preservar `settings` stale no `catch` (só zerar se nunca houve 200) + garantir `authFetch.ts:142` não expõe 401 ao caller quando `POST /api/auth/refresh` sucede.
- Mitigar race `StrictMode` double mount (`main.tsx:15`) + `AuthProvider` paralelo (`authStore.tsx:126`) com `AbortController`/`cancelled` e estabilizar deps `useCallback` (`[onSettingsChange, toast]` → `useRef`/memo) em `TelegramAlertsForm`; aplicar mesmo padrão mínimo no `MonitorStatusTab` (`useEffect` sem Abort).
- Garantir que reload de `/profile` com conta vinculada exiba `linked=true`, `telegramAlertsEnabled`, `linkedAt`, `botUsername` iguais ao `GET 200` sem interação extra, e que toggle Perfil↔Monitor permaneça sincronizado (`PATCH /users/me/telegram-settings` única coluna `User.telegram_alerts_enabled`).
- Adicionar testes: unit mockando `authFetch` 401 transitório→200 preservando `linked:true` + e2e Playwright reload `/profile` com mock `linked:true` (`data-testid="telegram-alerts-form"` → `Vinculado`).

## Capabilities

### New Capabilities
- (nenhuma) — correção de bug e robustez; não cria nova capability.

### Modified Capabilities
- `user-telegram-alerts`: requisito de que Perfil (e Monitor) reflita estado real de vínculo/opt-in no reload e não limpe estado vinculado em 401 transitório; adicionar cenários de 401 transitório vs 401 real (`notifyAuthSessionCleared`).

## Impact

- Frontend: `frontend/src/components/telegram/TelegramAlertsForm.tsx`, `frontend/src/components/monitor/MonitorStatusTab.tsx`, `frontend/src/lib/authFetch.ts`, `frontend/src/stores/authStore.tsx` (se guard necessário), `frontend/src/pages/ProfilePage.tsx` (se guard).
- Backend: sem alteração (`backend/app/routes/user_telegram.py:43`, `user_telegram_service.py:26`, `models.py:261` permanecem; critério de `linked` continua `bool(telegram_chat_id)`).
- Testes: `frontend/tests/e2e/visual-critical.spec.ts` (mock `telegram-settings` `linked:true`), novo unit `frontend/src/components/telegram/TelegramAlertsForm.test.tsx` ou similar, `backend/tests/` não afetado.
- Docs: `docs/monitor-telegram-alerts.md` sem alteração funcional (apenas referência se necessário); `openspec/specs/user-telegram-alerts/spec.md` recebe delta.
- Riscos: preservar stale pode ocultar `401 real` se distinção falhar; mitigado pelo critério 3 (refresh falha → logout prevalece) e `Abort` contra `StrictMode` race.
