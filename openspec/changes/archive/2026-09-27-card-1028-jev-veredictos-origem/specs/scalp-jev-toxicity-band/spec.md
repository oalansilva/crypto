## ADDED Requirements

### Requirement: Toxicity is read with two cut-offs and an uncertainty band

The toxicity reading of the reply (`book_toxic` noul) SHALL be labelled in the record with two cut-offs and an uncertainty band between them: below **0.4** the record SHALL label it not toxic; from **0.4** to **0.6** (inclusive at both ends) the record SHALL label it indeterminate; above **0.6** the record SHALL label it toxic. When the reply carries no noul value, the record SHALL label it unknown. The label SHALL be visible in the same cycle record that carries the gate verdicts.

#### Scenario: Below the lower cut-off

- **WHEN** the reply's noul is below 0.4
- **THEN** the record SHALL label the reading not toxic

#### Scenario: Inside the uncertainty band

- **WHEN** the reply's noul is between 0.4 and 0.6 inclusive
- **THEN** the record SHALL label the reading indeterminate — neither toxic nor not toxic

#### Scenario: Above the upper cut-off

- **WHEN** the reply's noul is above 0.6
- **THEN** the record SHALL label the reading toxic

#### Scenario: No noul in the reply

- **WHEN** the reply carries no noul value
- **THEN** the record SHALL label the reading unknown

### Requirement: The uncertainty band labels the record only and never changes the decision

The uncertainty band SHALL be record-only. The buy/sell decision SHALL keep today's single cut-off: the toxicity gate SHALL continue to refuse when noul is greater than or equal to **0.5**, exactly as before this change. A reading inside the uncertainty band SHALL be labelled indeterminate in the record while the decision continues to come from the 0.5 cut-off, so the record shows both the label and the decision value.

#### Scenario: Indeterminate reading keeps today's decision

- **WHEN** the reply's noul is inside the uncertainty band (for example 0.45)
- **THEN** the record SHALL label the reading indeterminate
- **AND** the toxicity gate SHALL decide exactly as today by the 0.5 cut-off (0.45 is not refused by the toxicity gate)

#### Scenario: The gate boundary is unchanged

- **WHEN** the reply's noul is exactly 0.5
- **THEN** the toxicity gate SHALL refuse as today (noul greater than or equal to 0.5 is toxic)
- **AND** the record SHALL label it indeterminate while showing the decision value

#### Scenario: The band does not alter any other gate

- **WHEN** the uncertainty band labelling is active
- **THEN** every other entry gate (confidence, cost, cost with slack, late) SHALL behave exactly as today
- **AND** the purchase/sell outcome for the same input SHALL be unchanged
