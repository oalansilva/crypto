## ADDED Requirements

### Requirement: The entry decision compares the position's band with the cycle's real cost, not a converted bp

The entry decision SHALL read the model reply as a **position on the ordered scale** and compare the **band of the level already reached** with the **real cost of that cycle**: below the cost, covers the cost, or covers the cost with slack. The band boundaries SHALL follow that cycle's real rate — the bare cost (`2 × fee_bp + spread_bp`) and the cost with slack (`× 1.5`) — reusing the existing cost comparisons; no band SHALL be fixed on the scale and no new threshold or constant SHALL be introduced.

#### Scenario: Position below the cost band is refused by cost, with a single reason

- **WHEN** the reply's level already reached sits below the cost band of that cycle and the confidence gate is not the one refusing (gate removed or confidence sufficient)
- **THEN** the cycle SHALL be refused by the cost rule with `skip_reason=hurdle` (a single reason)
- **AND** the lowest band SHALL NOT get a reason of its own

#### Scenario: Highest band passes the cost rule

- **WHEN** the reply's level already reached covers the cost with slack (the highest band)
- **THEN** the cycle SHALL pass the bare cost rule and the cost-with-slack rule
- **AND** it SHALL NOT be refused by cost

#### Scenario: Band that covers the cost without the slack

- **WHEN** the reply's level already reached covers the bare cost but not the cost with slack
- **THEN** the cycle SHALL be refused by the cost-with-slack rule with `skip_reason=regime`
- **AND** the bare cost rule SHALL be credited as passed

#### Scenario: Boundaries follow the cycle's own rate

- **WHEN** two cycles have different `fee_bp`/`spread_bp`
- **THEN** the same scale level SHALL fall in different bands according to each cycle's rate
- **AND** no band SHALL be a fixed value on the scale

#### Scenario: The comparison is the existing one

- **WHEN** the band of a level is computed
- **THEN** it SHALL reuse the existing cost comparisons (`passes_entry_hurdle`, strict `>`; `passes_regime_gate`, `>=`) with their current boundaries
- **AND** no new threshold or constant SHALL be introduced

### Requirement: A position between two scale points credits the level already reached

When the reply's score falls between two levels of the scale, the credited level SHALL be the **level already reached** (rounded down). The bp used by the cost comparison SHALL be the exact bp of that level of the scale, never a value interpolated between levels.

#### Scenario: Score between two levels rounds down

- **WHEN** the reply's score is 4.5
- **THEN** the credited level SHALL be level 4 (20 bp)
- **AND** the cost comparison SHALL use 20 bp, never 22.5 bp

#### Scenario: Only the whole level covering the cost passes

- **WHEN** the reply's score credits a level whose bp does not cover the cost
- **THEN** the cycle SHALL be refused by cost
- **AND** a fractional part above the credited level SHALL NOT be credited

#### Scenario: The scale keeps its ten levels

- **WHEN** the level already reached is read
- **THEN** the ten levels of the scale SHALL be unchanged
- **AND** the reading SHALL return one of those levels, never an in-between value

### Requirement: The question labels the ten scale options with the cycle's cost bands

The question asked to the model SHALL keep the **ten options** and the **position-on-the-scale** answer, and SHALL label each option with its band relative to that cycle's real cost (below the cost, covers the cost, covers with slack) instead of a bare number. The band label of each level SHALL be produced from the same cycle rate used by the decision, so the band the model sees and the band read by the decision agree.

#### Scenario: Ten options with band labels

- **WHEN** the question is built for a cycle
- **THEN** it SHALL carry the ten ordered options as today
- **AND** each option's label SHALL be its band relative to that cycle's cost
- **AND** the labels SHALL NOT be bare bp numbers alone

#### Scenario: The answer is still a position

- **WHEN** the reply chooses an option
- **THEN** the answer SHALL be read as the position (index) on the scale
- **AND** the band recorded SHALL be the band of the level already reached, matching the chosen option's label

#### Scenario: The question type is unchanged

- **WHEN** the question is built
- **THEN** the movement question SHALL keep the `score` type and the ten criteria of the scale
- **AND** no new question or answer type SHALL be introduced
