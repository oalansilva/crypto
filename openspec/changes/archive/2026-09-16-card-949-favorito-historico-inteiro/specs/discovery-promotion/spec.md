## ADDED Requirements

### Requirement: Promote after 70/30 writes the complete chosen period onto the favorite

When creating a tier 3 favorite from a Discovery result that was validated with walk-forward 70/30, the system SHALL set the favorite's operational `period_type` and start/end to the **complete period chosen for that sweep**, not the training slice stored on the result. For sweep period «todo» that operational window SHALL be first available candle → now. The persisted result, leaderboard Calmar, coverage and GO/NO-GO SHALL keep the training window. Provenance (`origin_type`, `sweep_id`, `result_id`, `strategy_identity_key`, `evidence_fingerprint`, `metrics_snapshot`) SHALL remain stored as the Discovery portrait and SHALL NOT be labeled on Favorites as the live full-period performance. The promotion modal SHALL NOT preview the complete period in this card.

#### Scenario: Promote todo after 70/30 does not inherit training end

- **GIVEN** a unique eligible result whose training evidence window is 17/08/2017 → 24/12/2023 and whose sweep period is «todo»
- **WHEN** the administrator confirms Promover as tier 3
- **THEN** the created favorite operational period is first candle → now
- **AND** the result row on Decide still shows the training window and 70/30 metrics
- **AND** the modal does not add a complete-period preview

#### Scenario: Discovery portrait stays on Discovery

- **WHEN** the operator returns to the sweep after promotion
- **THEN** Calmar, coverage and verdict of the grid remain the training values
- **AND** that portrait is not shown on `/favorites` as the new favorite's performance
