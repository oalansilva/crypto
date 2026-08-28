## ADDED Requirements

### Requirement: Profile Telegram alerts reflect persisted state on reload

The system SHALL display the persisted Telegram linkage and opt-in state on Profile (and Monitor) immediately after page reload without requiring user interaction, and SHALL NOT clear a previously successfully loaded linked state due to a transient 401 that is recovered via token refresh.

#### Scenario: Reload with linked account shows Vinculado

- **WHEN** a user with `telegram_chat_id` persisted (linked) and `telegram_alerts_enabled=true` reloads `/profile`
- **THEN** the UI SHALL show `Status: Vinculado`, the persisted `linkedAt` formatted `pt-BR`, `Bot: @<botUsername>` when `botUsername` is present, and the `Receber alertas Telegram` toggle in the on state — without requiring Save or Generate link.

#### Scenario: Transient 401 with successful refresh preserves linked state

- **WHEN** `GET /api/users/me/telegram-settings` initially returns 401 and `POST /api/auth/refresh` succeeds, causing `authFetch` to retry and receive 200 with `linked:true`
- **THEN** `TelegramAlertsForm` SHALL NOT set `settings` to `null` nor flash `Não vinculado` during the retry
- **AND** it SHALL render the 200 payload once available, keeping `loading` until the successful retry completes.

#### Scenario: Real 401 after failed refresh does not masquerade as linked

- **WHEN** `GET /api/users/me/telegram-settings` returns 401 and `POST /api/auth/refresh` fails (no refresh token, expired, or `notifyAuthSessionCleared` with `missing-refresh-token`/`refresh-failed`)
- **THEN** the session SHALL be cleared (logout) and Profile SHALL NOT preserve stale `linked:true` as if still linked
- **AND** subsequent unauthenticated access SHALL be treated as logged-out, not as a transient retry.

#### Scenario: Monitor toggle remains synchronized with Profile after reload

- **WHEN** the same user reloads `/profile` and separately loads `/monitor`, each page fetches `GET /api/users/me/telegram-settings`
- **THEN** both `TelegramAlertsForm` and `MonitorStatusTab` (`data-testid="monitor-telegram-alerts-toggle"`) SHALL reflect the same `telegram_alerts_enabled` value from the single `User.telegram_alerts_enabled` column
- **AND** a PATCH from either surface SHALL be visible on the other after reload.
