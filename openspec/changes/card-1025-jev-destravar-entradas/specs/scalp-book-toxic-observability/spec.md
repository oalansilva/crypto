## ADDED Requirements

### Requirement: The book_toxic drivers are recorded with the resulting flag

The diagnostic return record SHALL include the drivers of the `book_toxic` flag: the `noul` value returned by the model, the window features the decision used (`ret_bp`, `vol_bp`, `aggressor_flow`, `spread_bp_mean`, `trade_count`) and the resulting boolean. This SHALL make it possible to distinguish the model's own opinion from a wrong mapping. The record SHALL go to the #1015 diagnostic log only — no panel, route or status field — and the `noul ≥ 0,5` threshold SHALL NOT be retuned in this delivery.

#### Scenario: Drivers are recorded with the flag

- **WHEN** a Jev reply is mapped and the return record is written
- **THEN** the record SHALL contain the `noul` value returned by the model
- **AND** the window features used by the decision and the resulting `book_toxic` boolean

#### Scenario: Model opinion can be told apart from a wrong mapping

- **WHEN** the operator reads a toxic refusal over several days against the recorded drivers
- **THEN** the record SHALL allow telling whether the flag follows the model's own `noul` answer or an incorrect mapping
- **AND** the `aggressor_flow` of the window SHALL be available together with the flag

#### Scenario: The threshold is not retuned here

- **WHEN** this delivery is applied
- **THEN** the `noul ≥ 0,5` threshold used to derive `book_toxic` SHALL stay unchanged
- **AND** the toxic refusal token SHALL remain `toxic_book`

#### Scenario: Drivers stay out of the product surface

- **WHEN** the drivers are recorded
- **THEN** they SHALL appear only in the diagnostic log
- **AND** no panel field, route or status output SHALL gain them
