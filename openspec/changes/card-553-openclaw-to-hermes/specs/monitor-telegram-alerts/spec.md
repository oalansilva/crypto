## ADDED Requirements

### Requirement: Monitor Telegram scan does not read OpenClaw secrets
The Monitor Telegram scan job SHALL load bot token and destination from canonical Cripto/Hermes secret paths or environment, not from `/root/.openclaw/secrets` or an `openclaw-cron` identity.

#### Scenario: Scan runs without OpenClaw home
- **WHEN** `/root/.openclaw` is absent or unreadable
- **THEN** the scan still resolves configuration from the canonical path
- **AND** it SHALL NOT fail solely because OpenClaw home is missing
