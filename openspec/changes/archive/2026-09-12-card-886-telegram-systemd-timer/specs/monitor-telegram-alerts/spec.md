## ADDED Requirements

### Requirement: Product systemd timer wakes the daily Monitor Telegram scan
The daily Monitor Telegram alert scan SHALL be started by a product systemd oneshot+timer on the Cripto Farol host, without an LLM agent and without the Hermes cron as the wake path.

#### Scenario: Calendar fire runs the product scan
- **WHEN** the product timer fires at 08:05 BRT (OnCalendar 11:05 UTC)
- **THEN** the scan SHALL run `ops/run_monitor_telegram_alert_scan.py` with that environment's product env
- **AND** the journal of the unit SHALL record enviou, nada a enviar, or falhou
- **AND** the scan SHALL NOT depend on a Hermes/LLM process to start

#### Scenario: Hermes is not the product wake path
- **WHEN** the product timer is installed and enabled
- **THEN** the overlay SHALL list the product scan unit under `environments.*.services`
- **AND** the job Hermes `Monitor Telegram sinais diario` SHALL NOT be listed as product runtime

### Requirement: PROD install fires immediately from the 06/09/2026 baseline
Installing and enabling the PROD timer SHALL start one scan immediately and SHALL send DMs for sendable transitions since the last recorded scan state (PROD baseline 06/09/2026), respecting the existing anti-noise ceiling.

#### Scenario: Enable on PROD starts a scan without waiting for the next calendar
- **WHEN** the PROD oneshot+timer is enabled
- **THEN** one scan SHALL run immediately
- **AND** it SHALL NOT wait for the next 08:05 BRT

#### Scenario: Catch-up DMs since 06/09/2026
- **WHEN** the immediate PROD scan finds sendable position-aware transitions since 06/09/2026 for an eligible linked user
- **THEN** those DMs SHALL be sent via the existing Bot API path
- **AND** the existing anti-noise ceiling SHALL apply (overflow waits for a later scan)
- **AND** audit SHALL record `sent` or `failed`

### Requirement: DEV timer uses DEV env without the PROD bot
The DEV timer SHALL run against the DEV canonical env and SHALL NOT call the PROD bot, token, or webhook.

#### Scenario: DEV fire uses DEV env
- **WHEN** the DEV timer or its install-time oneshot runs
- **THEN** it SHALL source the DEV product env
- **AND** it SHALL NOT use PROD `MONITOR_TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, or the PROD webhook destination

### Requirement: Hermes cron is cut only after one green PROD timer run
The Hermes cron `Monitor Telegram sinais diario` SHALL be disabled or removed only after one PROD product-timer run that finished as enviou or nada a enviar (not falhou). After that cut there SHALL be a single daily wake.

#### Scenario: Cut after a green PROD run
- **WHEN** one PROD product-timer run has journaled enviou or nada a enviar
- **THEN** the Hermes cron `Monitor Telegram sinais diario` SHALL be disabled or removed
- **AND** there SHALL NOT be a second daily wake from Hermes plus the product timer

#### Scenario: Hermes stays until the first green PROD run
- **WHEN** the PROD product timer has not yet completed a green run
- **THEN** the Hermes cron MAY remain until that evidence exists
- **AND** the product SHALL NOT treat enabling that Hermes job as product runtime

### Requirement: Timer failure is journal-only
A failed product-timer run (timeout, exit ≠ 0, incomplete env) SHALL be visible in the unit journal and SHALL NOT send an extra Telegram DM that the clock broke.

#### Scenario: Failed fire does not DM clock-broke
- **WHEN** the product scan oneshot fails (timeout, non-zero exit, or incomplete env)
- **THEN** Alan SHALL NOT receive an extra Telegram DM about the broken clock
- **AND** the failure SHALL be in the unit journal

#### Scenario: Green and failed outcomes are journaled
- **WHEN** a product-timer run finishes
- **THEN** the journal SHALL show enviou, nada a enviar, or falhou without secrets
