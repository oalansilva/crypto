## ADDED Requirements

### Requirement: Promotion writes snapshot numbers onto the keys the Favorites grid already reads

When creating a tier 3 favorite from an eligible discovery result, the system SHALL copy Sharpe, negócios, win rate, retorno and Max DD from the snapshot da promoção onto the same keys the Favorites grid already reads. Profit Factor SHALL be copied when the discovery result already had it. Provenance (`origin_type`, `sweep_id`, `result_id`, `strategy_identity_key`, `evidence_fingerprint`, `metrics_snapshot`, promotion timestamp) SHALL remain stored. The client SHALL NOT supply or recompute those numbers.

#### Scenario: Promote writes grid-readable metrics and keeps provenance

- **WHEN** the administrator confirms promotion of an eligible unique result whose snapshot has Sharpe, negócios, win rate, retorno and Max DD
- **THEN** the created favorite's GET object contains those values on the keys the grade already reads
- **AND** varredura, result id, identity and the complete snapshot remain stored
- **AND** the result becomes `already_promoted`

#### Scenario: Nested-only snapshot is not enough

- **WHEN** a promotion would store the numbers only inside a nested envelope that the table ignores
- **THEN** the promotion is incomplete for this card
- **AND** the system SHALL also place the numbers on the keys the grade already reads
