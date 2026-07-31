## MODIFIED Requirements

### Requirement: User profile page exposes Binance credentials management
The system MUST provide Binance API credentials management on the authenticated user profile page (`/profile`). Credentials used for Wallet remain usable with read permission; credentials used for Monitor protective stop MUST be allowed to include Spot trading permission. The UI MUST NOT request withdraw permission and MUST continue to reject email/password values in the key/secret fields.

#### Scenario: Copy mentions optional Spot trading
- **WHEN** a logged-in user opens `/profile` Credenciais Binance
- **THEN** the UI MUST explain that read-only is enough for Home/Carteira and that Spot trading permission is required to use Proteger stop no Monitor
- **AND** the UI MUST recommend IP whitelist and MUST NOT ask for the Binance account password

#### Scenario: Secret is not re-displayed after save
- **WHEN** credentials are already configured and the user reloads `/profile`
- **THEN** the UI MUST NOT show the API Secret in clear text and MUST only show the masked API Key in the status area
