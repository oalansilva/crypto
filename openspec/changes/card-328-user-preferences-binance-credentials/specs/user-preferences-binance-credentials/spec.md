## ADDED Requirements

### Requirement: User preferences page exposes Binance credentials management
The system MUST provide an authenticated user preferences page where the logged-in user can view and manage their Binance read-only API credentials.

#### Scenario: Open preferences without credentials
- **WHEN** a logged-in user opens `/preferences` and has no Binance credentials saved
- **THEN** the page MUST show the Credenciais Binance block with status `Não configurada` and empty API Key / API Secret inputs

#### Scenario: Save read-only credentials
- **WHEN** the user submits a valid Binance API Key and API Secret on `/preferences`
- **THEN** the system MUST persist the credentials for that user via `/api/user/binance-credentials` and show status `Configurada` with a masked API Key

#### Scenario: Remove credentials
- **WHEN** the user removes Binance credentials from `/preferences`
- **THEN** the system MUST delete the stored credentials for that user and return the status to `Não configurada`

#### Scenario: Secret is not re-displayed after save
- **WHEN** credentials are already configured and the user reloads `/preferences`
- **THEN** the UI MUST NOT show the API Secret in clear text and MUST only show the masked API Key in the status area

### Requirement: Navigation exposes user preferences for every logged-in user
The authenticated app navigation MUST include an entry to the user preferences page that is distinct from admin system preferences.

#### Scenario: Account nav link
- **WHEN** a logged-in user views the main navigation
- **THEN** they MUST see a Preferências entry that navigates to `/preferences`

#### Scenario: Admin system preferences remain separate
- **WHEN** an admin views navigation
- **THEN** Preferências do sistema (`/system/preferences`) MUST remain available separately from user Preferências (`/preferences`)
