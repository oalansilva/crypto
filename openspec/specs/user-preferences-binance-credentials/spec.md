# user-preferences-binance-credentials Specification

## Purpose
Authenticated users manage Binance read-only API credentials from Meu Perfil.
## Requirements
### Requirement: User profile page exposes Binance credentials management
The system MUST provide Binance API credentials management on the authenticated user profile page (`/profile`). Credentials used for Wallet remain usable with read permission; credentials used for Monitor direct purchase, full-balance market sale or protective stop MUST be allowed to include Spot trading permission. The UI MUST NOT request withdraw permission and MUST continue to reject email/password values in the key/secret fields. The authenticated copy SHALL distinguish read-only (Home/Carteira) from Spot Trade (sem withdraw) for Operar, and SHALL NOT present the integration as read-only-only.

#### Scenario: Copy mentions optional Spot trading
- **Given** utilizador em Meu Perfil com bloco Credenciais Binance visível (critério 3)
- **WHEN** a logged-in user opens `/profile` Credenciais Binance
- **THEN** the UI MUST explain that read-only is enough for Home/Carteira and that Spot trading permission is required to use Comprar, Vender 100% or Proteger stop no Monitor
- **AND** the UI MUST recommend IP whitelist, MUST explicitly say not to enable withdraw, and MUST NOT ask for the Binance account password

#### Scenario: Open profile without credentials
- **Given** utilizador autenticado sem credenciais (critério 3)
- **WHEN** a logged-in user opens `/profile` and has no Binance credentials saved
- **THEN** the page MUST show the Credenciais Binance block with status `Não configurada` and empty API Key / API Secret inputs

#### Scenario: Save read-only credentials from profile
- **Given** utilizador com chaves válidas em mãos (critério 3)
- **WHEN** the user submits a valid Binance API Key and API Secret on `/profile`
- **THEN** the system MUST persist the credentials for that user via `/api/user/binance-credentials` and show status `Configurada` with a masked API Key

#### Scenario: Remove credentials from profile
- **Given** utilizador com credenciais configuradas (critério 3)
- **WHEN** the user removes Binance credentials from `/profile`
- **THEN** the system MUST delete the stored credentials for that user and return the status to `Não configurada`

#### Scenario: Secret is not re-displayed after save
- **Given** credenciais já configuradas (critério 3)
- **WHEN** credentials are already configured and the user reloads `/profile`
- **THEN** the UI MUST NOT show the API Secret in clear text and MUST only show the masked API Key in the status area

#### Scenario: Profile chrome does not claim read-only-only
- **Given** utilizador em Meu Perfil lê credenciais Binance (critério 3)
- **WHEN** a user reads `ProfilePage.tsx` header/chrome near Credenciais Binance
- **THEN** the copy SHALL NOT say “integração Binance read-only” or “Dados da conta e integração Binance read-only em um só lugar” as if the product only reads
- **AND** it SHALL say leitura para Home/Carteira e Spot Trade (sem withdraw) opcional para Operar no Monitor (e.g., “Credenciais Binance: leitura para Home/Carteira; Spot Trade (sem saque) opcional para Operar”)

#### Scenario: Toast and placeholder do not claim read-only-only
- **Given** utilizador em Meu Perfil salva/edita credenciais (critério 3)
- **WHEN** the user saves or edits credentials in `BinanceCredentialsForm.tsx`
- **THEN** the toast SHALL NOT say “Crie uma chave API read-only na Binance”
- **AND** the placeholder/label for API Secret SHALL NOT say “API Secret da chave read-only”
- **AND** the helper texts SHALL distinguish leitura para Carteira/Home vs Spot Trading para proteger stop ou operar no Monitor, always without withdraw

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

