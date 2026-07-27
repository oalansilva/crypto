## ADDED Requirements

### Requirement: Wallet shows credential status and links to user preferences
The external balances (Carteira) page MUST NOT be the primary place to edit Binance API Key/Secret. It MUST show whether credentials are configured and direct the user to `/preferences` to manage them.

#### Scenario: Credentials not configured on wallet
- **WHEN** the user opens `/external/balances` without Binance credentials
- **THEN** the page MUST show status `Não configurada` and a clear action/link to configure credentials in Preferências

#### Scenario: Credentials configured on wallet
- **WHEN** the user opens `/external/balances` with Binance credentials configured
- **THEN** the page MUST show status `Configurada` (optionally with masked API Key) and still allow navigating to Preferências to change or remove them

#### Scenario: Wallet continues using per-user credentials
- **WHEN** the user has credentials saved in Preferências
- **THEN** the wallet balances snapshot MUST continue to use the logged-in user's Binance credentials without requiring re-entry on the wallet page
