# monitor-telegram-favorite-toggle Specification

## Purpose
Admin control for Monitor Telegram eligibility per catalog favorite strategy.

## Requirements
### Requirement: Admin controls Telegram alert eligibility per favorite
The system SHALL allow an admin to mark each catalog favorite strategy as eligible or ineligible for Monitor Telegram alerts.

#### Scenario: Admin enables Telegram notification for a favorite
- **WHEN** an admin updates a favorite with `notify_telegram=true`
- **THEN** the system SHALL persist the favorite as eligible for Monitor Telegram alerts
- **AND** subsequent Favorites API responses SHALL include `notify_telegram=true`

#### Scenario: Admin disables Telegram notification for a favorite
- **WHEN** an admin updates a favorite with `notify_telegram=false`
- **THEN** the system SHALL persist the favorite as ineligible for Monitor Telegram alerts
- **AND** subsequent Favorites API responses SHALL include `notify_telegram=false`

#### Scenario: Common user cannot change catalog notification eligibility
- **WHEN** a common user sees an admin catalog favorite
- **AND** attempts to update `notify_telegram`
- **THEN** the system SHALL reject the update

### Requirement: Telegram scan uses explicit favorite eligibility
Monitor Telegram alert scans SHALL evaluate only catalog favorite strategies where `notify_telegram=true`.

#### Scenario: Unstarred enabled favorite remains eligible by default
- **WHEN** a catalog favorite has `notify_telegram=true`
- **AND** no explicit Monitor Telegram tier filter is configured
- **THEN** the Monitor Telegram scan SHALL evaluate that favorite even when it has no tier/star classification

#### Scenario: Disabled favorite is excluded from alert scan
- **WHEN** a catalog favorite has `notify_telegram=false`
- **THEN** the Monitor Telegram scan SHALL NOT evaluate that favorite as an alert candidate

#### Scenario: Enabled favorite remains eligible for alert scan
- **WHEN** a catalog favorite has `notify_telegram=true`
- **THEN** the Monitor Telegram scan SHALL evaluate that favorite, subject to existing alert status, dedupe, rate-limit, allowlist, and dry-run rules
