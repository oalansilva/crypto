# user-preferences-binance-credentials Specification

## Purpose
Authenticated users manage Binance read-only API credentials from Meu Perfil.

## Requirements
### Requirement: User profile page exposes Binance credentials management
The system MUST provide Binance read-only API credentials management on the authenticated user profile page (`/profile`), reachable from the account control in the app bar.

#### Scenario: Open profile without credentials
- **WHEN** a logged-in user opens `/profile` and has no Binance credentials saved
- **THEN** the page MUST show the Credenciais Binance block with status `Não configurada` and empty API Key / API Secret inputs

#### Scenario: Save read-only credentials from profile
- **WHEN** the user submits a valid Binance API Key and API Secret on `/profile`
- **THEN** the system MUST persist the credentials for that user via `/api/user/binance-credentials` and show status `Configurada` with a masked API Key

#### Scenario: Remove credentials from profile
- **WHEN** the user removes Binance credentials from `/profile`
- **THEN** the system MUST delete the stored credentials for that user and return the status to `Não configurada`

#### Scenario: Secret is not re-displayed after save
- **WHEN** credentials are already configured and the user reloads `/profile`
- **THEN** the UI MUST NOT show the API Secret in clear text and MUST only show the masked API Key in the status area

### Requirement: Account bar opens profile for credential management
The authenticated account control in the app bar MUST continue to expose Meu Perfil as the entry point for account settings including Binance credentials. The app MUST NOT require a separate user Preferências nav item for this capability.

#### Scenario: Account bar entry
- **WHEN** a logged-in user opens the account menu in the app bar
- **THEN** they MUST be able to navigate to `/profile` (Meu Perfil) where Credenciais Binance are managed

#### Scenario: Legacy preferences route redirects
- **WHEN** a logged-in user opens `/preferences`
- **THEN** the app MUST redirect them to `/profile`

#### Scenario: Admin system preferences remain separate
- **WHEN** an admin views navigation
- **THEN** Preferências do sistema (`/system/preferences`) MUST remain available separately from Meu Perfil
