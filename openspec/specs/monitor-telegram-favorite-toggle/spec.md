# monitor-telegram-favorite-toggle Specification

## Purpose
Admin control for Monitor Telegram eligibility per catalog favorite strategy.
## Requirements
### Requirement: Admin controls Telegram alert eligibility per favorite
The system SHALL let the owner of a favorite, admin or not, switch its Telegram alert on or off (`notify_telegram`) in any class, **only from the Monitor** (card #1122, Alan's decision of 27/10/2026). The alert is on by default (`notify_telegram=true` on every creation path) and only has effect while the favorite has at least one star. Giving the first star to an unstarred favorite SHALL switch its alert on in the same write; changing between 1, 2 and 3 stars SHALL NOT change it. A user MUST NOT change the alert of a favorite he does not own. Favoritos SHALL NOT show any alert control: no "Alertar" column, no bell in the Ações cell, no "Alertar: on/off" on mobile cards and no "Fora da carteira: sem alerta" notice.

In the Monitor, every own starred strategy SHALL show the control (`monitor-multiclass`): a switch (`role="switch"`, `aria-checked`) with the visible text "Alerta" and the state, whose accessible name includes the asset, timeframe, strategy and, for ação/ETF, the short configuration, in the row actions (1280 px and wider), in the Status cell from 1024 to 1279 px, in the mobile card (44 px target) and in the detail. Unstarred favorites do not appear in the Monitor, so there is no unstarred row state; catalog rows SHALL show "Catálogo · sem alerta", without a control.

#### Scenario: Owner switches the alert off in the Monitor
- **WHEN** a common user switches off the alert of his own ETH/USDT 4h favorite in the Monitor
- **THEN** the system SHALL persist `notify_telegram=false`
- **AND** subsequent Monitor responses SHALL include `notify_telegram=false`
- **AND** the switch SHALL read "Alerta" with the state "desligado" and `aria-checked="false"`

#### Scenario: New favorite starts with the alert on
- **WHEN** a favorite is created from a result, a batch or the Descoberta
- **THEN** it SHALL have `notify_telegram=true`

#### Scenario: First star switches the alert on
- **WHEN** the owner gives 1 star to his unstarred QQQ favorite whose alert is off
- **THEN** the system SHALL persist `tier=3` and `notify_telegram=true`

#### Scenario: Favoritos has no alert control
- **WHEN** the owner opens Favoritos at 1440, 1280, 1024 or 390 px
- **THEN** no "Alertar" column, bell or "Alertar: on/off" control SHALL be shown
- **AND** no "Fora da carteira: sem alerta" notice SHALL be shown

#### Scenario: User cannot change the alert of a catalog favorite he sees
- **WHEN** a user attempts to update `notify_telegram` of an admin catalog favorite that is visible to him
- **THEN** the system SHALL reject the update with 403 and change nothing

#### Scenario: User cannot change the alert of a favorite he does not see
- **WHEN** a user attempts to update `notify_telegram` of a favorite owned by someone else that is not visible to him
- **THEN** the system SHALL answer 404, without revealing that the favorite exists, and change nothing

### Requirement: Telegram scan uses explicit favorite eligibility
Monitor Telegram alert scans SHALL evaluate, for each eligible user, only that user's own favorites with at least one star (`tier` 1, 2 or 3) and `notify_telegram=true`. The system tier filter (`monitor_telegram_tier_filter`) SHALL NOT change eligibility.

#### Scenario: Unstarred favorite is not eligible
- **WHEN** a user's own favorite has `notify_telegram=true` and no star
- **THEN** the scan SHALL NOT evaluate that favorite as an alert candidate

#### Scenario: Switched-off favorite is excluded from alert scan
- **WHEN** a starred favorite has `notify_telegram=false`
- **THEN** the scan SHALL NOT evaluate that favorite as an alert candidate

#### Scenario: Starred favorite with the alert on is eligible
- **WHEN** a user's own favorite has 1, 2 or 3 stars and `notify_telegram=true`
- **THEN** the scan SHALL evaluate that favorite for its owner, subject to event identity, data health and dry-run rules, regardless of the portfolio

