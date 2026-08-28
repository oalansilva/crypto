# user-telegram-alerts Specification

## Purpose
TBD - created by archiving change card-747-position-telegram-dm. Update Purpose after archive.
## Requirements
### Requirement: User Telegram delivery parameters
The system SHALL let each user declare Telegram contact parameters in Profile and SHALL use bot linking to resolve the deliverable chat id.

#### Scenario: User saves Telegram username in Profile
- **WHEN** an authenticated user saves their Telegram `@username` in Profile alerts settings
- **THEN** the system SHALL persist the normalized username (without `@`)
- **AND** the system SHALL require username before generating a link token

#### Scenario: Linked chat id is the delivery destination
- **WHEN** the user completes `/link <token>` with the Cripto Farol bot
- **THEN** the system SHALL persist `telegram_chat_id` from the Telegram update
- **AND** position-aware alerts SHALL be sent to that chat id

#### Scenario: Username mismatch after link is surfaced safely
- **WHEN** the linked Telegram account username differs from the username declared in Profile
- **THEN** the system SHALL still complete linking using `chat_id`
- **AND** Profile SHALL show a non-blocking warning that declared and linked usernames differ

### Requirement: User can enable or disable Telegram alerts in Profile and Monitor preferences
The system SHALL expose the same opt-in flag in Profile and Monitor preferences.

#### Scenario: Toggle in Profile updates opt-in
- **WHEN** a user enables or disables Telegram alerts in Profile
- **THEN** the system SHALL update `telegram_alerts_enabled` for that user
- **AND** the cron SHALL include or exclude that user accordingly

#### Scenario: Toggle in Monitor preferences mirrors Profile
- **WHEN** a user toggles "Receber alertas Telegram" in Monitor global preferences
- **THEN** the system SHALL update the same `telegram_alerts_enabled` flag
- **AND** Profile SHALL reflect the same state on next load

#### Scenario: Disabled user receives no alerts even when linked
- **WHEN** a user is linked but has `telegram_alerts_enabled=false`
- **THEN** the system SHALL NOT send position-aware alerts to that user

### Requirement: Telegram webhook is owned by Cripto Farol
Telegram bot updates for account linking SHALL be processed by the Cripto Farol backend without routing through Hermes.

#### Scenario: Webhook validates secret
- **WHEN** Telegram posts an update to the Cripto Farol webhook endpoint
- **THEN** the system SHALL validate the configured webhook secret before processing
- **AND** invalid requests SHALL be rejected

#### Scenario: Bot token is loaded from Cripto configuration only
- **WHEN** the alert scanner or webhook handler needs the bot token
- **THEN** it SHALL load from Cripto environment or Cripto-owned secrets file
- **AND** it SHALL NOT depend on `/root/.hermes/secrets/` or Hermes services

### Requirement: User Telegram link privacy
The system SHALL store Telegram linkage per user and SHALL NOT expose one user's chat destination to other users.

#### Scenario: Profile shows only own link status
- **WHEN** a user views Profile Telegram alerts
- **THEN** they SHALL see only their own link status and opt-in state
- **AND** they SHALL NOT see other users' chat ids

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

