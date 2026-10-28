## MODIFIED Requirements

### Requirement: Alert anti-noise controls
The system SHALL prevent repeated Monitor Telegram alerts through event identity **per user**, for signal alerts, data-delay warnings and the transition notice. A signal event is identified by user, favorite, new reading and the start of the closed candle that produced it; a data-delay warning by user, data source, asset and delay episode; the transition notice by user. The time-based minimum repeat window SHALL NOT decide duplicates anymore. Signal alerts and data-delay warnings of a scan SHALL NOT be capped by the per-user rate limit (Alan's decision 4, 26/10/2026): each one is its own message. The scan SHALL NOT send any operational Binance wallet notice (card #1122, 27/10/2026: the wallet no longer decides alerts), so the configurable rate limit (`monitor_telegram_rate_limit_count` / `monitor_telegram_rate_limit_window_minutes`) has no use in the scan.

#### Scenario: Same event is skipped per user
- **WHEN** an alert with the same event key was already reserved, sent or dry-run for that user
- **THEN** the system SHALL skip sending it again
- **AND** it SHALL report the skip reason as duplicate

#### Scenario: Scan alerts are not rate limited
- **WHEN** seven favorites of a user, starred and with the alert on, change reading in the same scan and the configured limit is 5 messages per 60 minutes
- **THEN** the system SHALL send seven messages to that user, one per favorite
- **AND** it SHALL NOT report any of them as rate limited

#### Scenario: No operational wallet notice
- **WHEN** a user's Binance wallet is unavailable during a scan
- **THEN** the scan SHALL NOT send an operational wallet DM to that user

## REMOVED Requirements

### Requirement: Position-aware Monitor Telegram alerts per user
**Reason**: Card #1122, decisão de Alan de 27/10/2026: a carteira não decide quem recebe. Entrada e saída saem com ou sem o ativo na carteira, em cripto, ação e ETF; a cripto perde a supressão da reentrada com saldo e a da saída sem saldo.
**Migration**: `favorite-telegram-alerts` ("Entrada e saída saem com ou sem o ativo na carteira" e "Alertas saem das estratégias que cada usuário acompanha no Monitor"). A mensagem segue "Mensagem identifica estratégia e configuração e não é ordem", com `Motivo=Stop` na saída por stop.

### Requirement: Em portfólio scope resolution per user
**Reason**: A varredura não usa mais o escopo "Em portfólio" para decidir alertas (decisão de Alan de 27/10/2026).
**Migration**: O Monitor continua resolvendo "Em portfólio" para a tela (tag "Carteira", filtro e indicador), sem efeito no Telegram (`monitor-multiclass`).

### Requirement: Binance unavailability operational alert per user
**Reason**: Sem a carteira na decisão, a varredura não lê a carteira Binance e não há alerta a pausar; o aviso operacional sai (card #1122, 27/10/2026).
**Migration**: `favorite-telegram-alerts` ("Carteira Binance fora da varredura").
