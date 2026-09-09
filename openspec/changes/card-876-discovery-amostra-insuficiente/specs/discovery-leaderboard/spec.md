## ADDED Requirements

### Requirement: Persist inspectable insufficient-sample results

For each combination cut by the listing gate the system SHALL persist a `DiscoveryResult` with `eligibility=insufficient_sample` (never `low_sample` or `eligible`), `rank` null, and ranking metrics (`calmar_ratio`, `max_drawdown`, `trades_count`, coverage used for ranking) stored as null so the UI shows `N/A`. The result SHALL remain in the default Decidir list (not omitted as discarded). It SHALL NOT receive a ranked position and SHALL NOT occupy Acompanhar top-5 partials.

#### Scenario: Short listing appears on Decidir without rank

- **WHEN** a combination settles as `insufficient_sample`
- **THEN** a result row exists for that symbol × timeframe × template
- **AND** `eligibility` is `insufficient_sample`
- **AND** rank is null and Calmar/drawdown/trades are null

#### Scenario: Insufficient sample stays out of top-5

- **WHEN** Acompanhar requests locked top-5 partials
- **THEN** no `insufficient_sample` row is included
- **AND** eligible (and, if no eligible, existing `low_sample`) ordering is unchanged

## MODIFIED Requirements

### Requirement: Gate ranking and promotion eligibility by sample quality

The default eligibility policy SHALL require at least `30` closed trades and `90%` candle coverage of the requested effective window. For Discovery walk-forward 70/30, the requested effective window SHALL be the in-sample (train) interval persisted on the result, not the unused sweep snapshot span. The thresholds SHALL be configuration/versioned and persisted with the result. Ineligible optimizer results SHALL remain inspectable with a `Baixa amostra` badge and reason, SHALL have no ranked position, and SHALL not be promotable until a later versioned reclassification makes them eligible. Listing-gate results SHALL use `eligibility=insufficient_sample` and the visible badge `Amostra insuficiente`; they SHALL NOT reuse the `Baixa amostra` badge or `low_sample` eligibility. The Combo walk-forward GO/NO-GO profile (including the 100-trade in-sample floor) SHALL NOT replace this Discovery eligibility policy.

#### Scenario: Low sample candidate

- **WHEN** a successful result has 18 trades or 82% coverage
- **THEN** it is shown as `Baixa amostra`, receives no rank and cannot be promoted
- **AND** its metrics are not merged into eligible ordering

#### Scenario: Discovery eligibility uses in-sample sample quality

- **WHEN** a Discovery walk-forward result has at least 30 in-sample closed trades and at least 90% coverage of the train window
- **THEN** it MAY be eligible even if the holdout is `NO-GO` or `ERROR`
- **AND** it SHALL NOT be required to meet Combo walk-forward minima (100 in-sample trades / Sharpe 0.8) to rank

#### Scenario: Insufficient sample is not baixa amostra

- **WHEN** a result was cut before the optimizer because train bars < 30
- **THEN** the visible badge is `Amostra insuficiente`
- **AND** the badge is not `Baixa amostra`
- **AND** the result is not ranked and not promotable

### Requirement: Action column always exposes promote and discard when allowed

Each visible non-promoted row whose eligibility is `eligible` or `low_sample` SHALL show a Promote control (enabled only when unique and eligible; otherwise visible and disabled with reason) **and** a Discard control. An `already_promoted` row SHALL show the promoted state and SHALL NOT show Discard. Promote MUST NOT be hidden solely because `low_sample` eligibility failed. A row with `eligibility=insufficient_sample` SHALL NOT show a Promote control (no CTA) and SHALL keep Discard when discard is otherwise allowed.

#### Scenario: Low sample still shows both actions

- **WHEN** a row is `Baixa amostra`
- **THEN** Promote is visible and disabled with the sample reason
- **AND** Excluir is visible and enabled

#### Scenario: Insufficient sample has no promote CTA

- **WHEN** a row is `Amostra insuficiente`
- **THEN** no Promover control is rendered
- **AND** the operator cannot promote that row
- **AND** Excluir remains available
