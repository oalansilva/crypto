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

