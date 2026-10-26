## MODIFIED Requirements

### Requirement: Admin controls Telegram alert eligibility per favorite
The system SHALL allow the owner of a favorite, admin or not, to mark it "Alertar" (`notify_telegram=true`) or unmark it, in any class. A user MUST NOT change the mark of a favorite he does not own, including an admin catalog favorite seen through the Monitor fallback. In Favoritos, the column header SHALL be "Alertar" for every owner, shown from 1280 px; from 1024 to 1279 px the column is hidden and the same control (bell, `aria-pressed`) SHALL sit in the Ações cell; on mobile cards the control SHALL read "Alertar: on" / "Alertar: off" with a 44 px target. Every control, crypto rows included, SHALL carry `aria-label` "Alertar no Telegram: ligado/desligado" from page load. When "Alertar" is on for an ação or ETF favorite whose asset is not in the owner's portfolio, the row SHALL show "Fora da carteira: sem alerta. Marque o ativo como "No portfólio" no Monitor". Catalog rows seen through the fallback MUST show no control.

#### Scenario: Owner enables Alertar on NVDA
- **WHEN** a common user updates his own NVDA favorite with `notify_telegram=true`
- **THEN** the system SHALL persist the mark
- **AND** subsequent Favorites and Monitor responses SHALL include `notify_telegram=true`

#### Scenario: Notebook at 1180 px
- **WHEN** the owner opens Favoritos at 1180 px
- **THEN** the "Alertar" column SHALL be hidden and the control SHALL appear in the Ações cell
- **AND** the strategy column SHALL keep the name, configuration and refresh status readable

#### Scenario: Ação marked outside the portfolio
- **WHEN** SPY has "Alertar" on and SPY is not in the owner's portfolio
- **THEN** the SPY row SHALL show "Fora da carteira: sem alerta"

#### Scenario: Owner disables Alertar
- **WHEN** the owner updates a favorite with `notify_telegram=false`
- **THEN** the system SHALL persist the favorite as not alerting
- **AND** subsequent Favorites API responses SHALL include `notify_telegram=false`

#### Scenario: User cannot change the mark of a catalog favorite he sees
- **WHEN** a user attempts to update `notify_telegram` of an admin catalog favorite that is visible to him
- **THEN** the system SHALL reject the update with 403 and change nothing

#### Scenario: User cannot change the mark of a favorite he does not see
- **WHEN** a user attempts to update `notify_telegram` of a favorite owned by someone else that is not visible to him
- **THEN** the system SHALL answer 404, without revealing that the favorite exists, and change nothing

### Requirement: Telegram scan uses explicit favorite eligibility
Monitor Telegram alert scans SHALL evaluate, for each eligible user, only that user's own favorites where `notify_telegram=true`.

#### Scenario: Unstarred marked favorite remains eligible by default
- **WHEN** a user's own favorite has `notify_telegram=true`
- **AND** no explicit Monitor Telegram tier filter is configured
- **THEN** the scan SHALL evaluate that favorite for its owner even when it has no tier/star classification

#### Scenario: Unmarked favorite is excluded from alert scan
- **WHEN** a favorite has `notify_telegram=false`
- **THEN** the scan SHALL NOT evaluate that favorite as an alert candidate

#### Scenario: Marked favorite remains eligible for alert scan
- **WHEN** a user's own favorite has `notify_telegram=true`
- **THEN** the scan SHALL evaluate that favorite for its owner, subject to event identity, portfolio and dry-run rules
