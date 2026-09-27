## ADDED Requirements

### Requirement: A cycle with a model reply records the verdict of every signal-fed entry gate in the same record

For every scalp cycle that received a reply from the model, the Farol SHALL write a single cycle record carrying the verdict of **each** entry gate that reads the reply — the cost gate (`hurdle`), the cost-with-slack gate (`regime`), the toxicity gate (`toxic_book`) and the confidence gate (`low_confidence`), plus the late gate (`jev_late`) and the direction gate (`hold`). Each verdict SHALL be `pass`, `fail` or `not_applicable`, computed independently of the first gate that closed the cycle, so a cycle refused by an earlier gate (for example confidence) still shows the verdict of the later gates (cost, cost with slack, regime, toxicity). The record SHALL keep the first refusal token as `skip_reason` (raw token, no free-text rewriting). A cycle that passes every gate and sends an order SHALL also leave this record, with the verdicts of the same gates. The record SHALL be written to the same diagnostic log file as the existing call records; the sizing gates that do not read the reply (`t_zero`, `ceiling_reduce_only`, `zero_inventory`, `would_cross`, `dust`) SHALL be outside this record in this delivery.

#### Scenario: A cycle refused by confidence still shows cost, slack and toxicity verdicts

- **WHEN** a cycle has a model reply whose confidence is below the threshold and the confidence gate closes the cycle first
- **THEN** the cycle record SHALL contain the verdict of the cost gate (`hurdle`), the cost-with-slack/regime gate (`regime`) and the toxicity gate (`toxic_book`) for that same cycle
- **AND** the record SHALL keep `skip_reason=low_confidence` as the first refusal token

#### Scenario: A sent cycle leaves the verdict record

- **WHEN** a cycle has a model reply and passes every entry gate so an order is sent
- **THEN** the log SHALL contain a cycle record with the verdicts of the cost, cost-with-slack, regime, toxicity and confidence gates
- **AND** the record SHALL show no first refusal token (`skip_reason=none`)

#### Scenario: Every evaluated gate has one verdict

- **WHEN** a cycle record is written after a model reply
- **THEN** each of the `hurdle`, `regime`, `toxic_book`, `low_confidence`, `jev_late` and `hold` gates SHALL appear with exactly one of `pass`, `fail` or `not_applicable`
- **AND** a gate that is configured off (for example the confidence gate removed) SHALL be `not_applicable`, never `fail`

### Requirement: The cycle record states the origin of the confidence used

The cycle record and the call return record SHALL state where the confidence number used by the decision came from: the confidence field of the reply (`reply_field`), the probability of the chosen option (`choice_probability`) or, when neither exists, `none`. The value and its origin SHALL be produced by the same computation, so the recorded origin is the origin of the exact value the decision consumed.

#### Scenario: Reply carries the confidence field

- **WHEN** the reply's side answer carries a `confidence` field
- **THEN** the record SHALL show that value with origin `reply_field`

#### Scenario: Reply omits the confidence field

- **WHEN** the reply's side answer has no `confidence` field and the chosen option has a probability
- **THEN** the record SHALL show the chosen option's probability with origin `choice_probability`

#### Scenario: No confidence at all

- **WHEN** the reply carries neither a confidence field nor a probability for the chosen option
- **THEN** the record SHALL show origin `none` and the confidence used SHALL be the same as today

### Requirement: The decision outcome does not change

The verdict computation and the new record fields SHALL be side effects: for the same input, the resulting decision (`send` or the first `skip_reason`) SHALL be the same as before this change. The order of the entry gates and the gate that closes the cycle first SHALL NOT change.

#### Scenario: Same input, same decision

- **WHEN** the same cycle input is evaluated before and after this change (a confidence refusal, a cost refusal, a regime refusal, a toxic refusal, a late refusal and a fully green cycle)
- **THEN** the resulting decision (`send` flag and first `skip_reason`) SHALL be identical in both cases
- **AND** only the log record SHALL differ

#### Scenario: The first refusal is still the first refusal

- **WHEN** two gates would both fail (for example confidence and cost)
- **THEN** the cycle SHALL close with the same first `skip_reason` as today
- **AND** the record SHALL still show the verdict of the other failing gate

### Requirement: The verdict record is log-only

The verdict record SHALL go to the diagnostic log file only. It SHALL NOT add or change anything in the Monitor panel, in `/api/scalp/status`, in any route or HTML, in the database, or in any export/Drive surface. The diagnostic log file, its single-file ceiling and its tail truncation SHALL stay as delivered by the diagnostic log of this project.

#### Scenario: No product surface gains the verdicts

- **WHEN** cycles are evaluated with the verdict record active
- **THEN** the Monitor panel and `/api/scalp/status` SHALL NOT gain the gate verdicts, the confidence origin or the model version
- **AND** no new route, HTML or database table SHALL be introduced

#### Scenario: The record lives in the existing diagnostic file

- **WHEN** the verdict record is written
- **THEN** it SHALL be written to the diagnostic log file already used for the scalp Jev calls
- **AND** the file SHALL keep its single file with the size ceiling and the oldest-first tail truncation
