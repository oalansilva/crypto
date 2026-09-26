## ADDED Requirements

### Requirement: Each Jev call logs its entry and return

For every TypeSafe/SystemOne (`/v1/systemone`) call made by the directional scalp, the Farol SHALL write a diagnostic entry record with the payload sent (`state` and `questions`: touch, window, account, resting) and a return record with the reply (side, `expected_move_bp` score/bp, `book_toxic`, confidence, latency and HTTP status). On HTTP or transport error the return record SHALL include a summarized (truncated) error body. Entry and return SHALL be readable in the log file and correlatable to the same call. Successful calls SHALL be logged at level INFO; errors at level WARNING. Successful calls SHALL NOT stay invisible as they are today.

#### Scenario: Complete call appears with entry and return

- **WHEN** the scalp sends one Jev request and receives a reply
- **THEN** the log file SHALL contain a readable entry record with the payload sent (touch, window, account summary, resting, questions)
- **AND** a readable return record with side, expected_move_bp/score, book_toxic, confidence, latency and the HTTP status of the reply

#### Scenario: Error call logs summarized body

- **WHEN** the Jev call fails with an HTTP error or a transport error
- **THEN** the return record SHALL be logged at level WARNING
- **AND** SHALL include the HTTP status (or transport failure) and a summarized, truncated, secret-redacted error body

#### Scenario: Return carries the decision inputs

- **WHEN** the Jev reply is mapped to a signal
- **THEN** the return record SHALL show the confidence, the expected move in bp and the book_toxic answer together with the latency
- **AND** SHALL NOT require reading panel counters to recover them

### Requirement: Account in the log is summarized and no secret is ever logged

The entry record SHALL summarize the account as booleans only — «is there a position?» / «is there balance?» (`has_position`, `has_balance`) — and SHALL NOT contain exact balance or position values (for example `inventory_btc`, `t`, `remaining_to_t`, free USDT or free BTC). No secret SHALL appear in any record: neither the TypeSafe/Jev API key nor any token, nor the `Authorization` header value. Error bodies SHALL be summarized and secret-redacted before being written. The wire payload sent to Jev SHALL be unchanged — redaction and summarization happen only when formatting the log record.

#### Scenario: Entry log never shows exact balances or positions

- **WHEN** an entry record is written for a call whose payload contains `inventory_btc`, `t` and `remaining_to_t`
- **THEN** the record SHALL contain only `has_position` and `has_balance` for the account
- **AND** SHALL NOT contain those exact values or any free balance value

#### Scenario: Key echoed by an error body is redacted

- **WHEN** an error body echoes the TypeSafe API key or another configured secret
- **THEN** the written record SHALL show the secret redacted
- **AND** no record SHALL contain the `Authorization` header value

#### Scenario: Panel stays untouched

- **WHEN** cycles are refused and the diagnostic log grows
- **THEN** the Monitor panel and `/api/scalp/status` SHALL NOT gain the last refusal reason or any diagnostic field
- **AND** no secret SHALL appear in the panel or in any register

### Requirement: A cycle refused by a gate logs its skip_reason

When a scalp cycle is refused by a gate — that is, the cycle ends without an order and its `skip_reason` is non-null — the Farol SHALL log the `skip_reason` token of the gate that refused the cycle (for example `hold`, `low_confidence`, `hurdle`, `toxic_book`, `jev_late`, `jev_target`, `t_zero`, `ceiling_reduce_only`, `window_empty`, `switch_off`, `halted`, `no_book` «livro indisponível»). The token SHALL be logged as-is (no free-text rewriting) and SHALL cover both refusals before the Jev call and refusals after the reply. This record SHALL go to the log file only. Cycles that end without an order but **without** a gate token — a decided order rejected by the broker, a `send=True` intent with no `live_send` (keyless stand-in), or `rest_open` blocking the send — are outside this requirement and SHALL leave no diagnostic record in this file.

#### Scenario: Post-reply gate refusal is visible

- **WHEN** the Jev reply arrives and a gate such as hurdle, confidence or toxic book refuses the entry
- **THEN** the log SHALL contain a record with that `skip_reason` token (e.g. `hurdle`, `low_confidence`, `toxic_book`)
- **AND** the operator SHALL be able to tell which gate refused without reading panel counters

#### Scenario: Pre-call refusal is visible

- **WHEN** the cycle is refused before any Jev call (e.g. `window_empty`, `no_book`, `jev_target`, `switch_off`, `halted`)
- **THEN** the log SHALL contain a record with that `skip_reason` token
- **AND** the cycle SHALL behave exactly as today (no call, no order)

#### Scenario: Every gate-refused cycle leaves its gate

- **WHEN** any cycle is refused by a gate (it ends without an order and its `skip_reason` is non-null)
- **THEN** the log SHALL contain exactly which gate refused it via the `skip_reason` token

### Requirement: Configurable log level with trading behavior unchanged

The diagnostic log level SHALL be configurable (entry/return at INFO, errors at WARNING) so the log does not flood production. Enabling, disabling or configuring this logging SHALL NOT change the Jev consult cadence (~1 s / `JEV_TARGET_MS`), the entry hurdle (`expected_move_bp` greater than `2 × fee_bp + spread_bp`), the exit target (35 bp) or stop (−28 bp), the 1.5 s Jev late/timeout fail-closed (`JEV_LATE_MS`), the 500 ms book-freshness fail-closed (`age_ms`), or any trading decision. The payload sent to Jev SHALL be unchanged.

#### Scenario: Level is configurable

- **WHEN** the operator raises the diagnostic log level via configuration
- **THEN** the per-call entry/return and refusal records SHALL stop being written at the lowered verbosity
- **AND** error records SHALL keep their WARNING severity semantics

#### Scenario: Logging does not alter decisions

- **WHEN** diagnostic logging is active across many cycles
- **THEN** the same payload as today SHALL be sent to Jev
- **AND** the same gates and constants SHALL apply (cadence ~1 s, hurdle, 1.5 s fail-closed, 500 ms freshness fail-closed, target 35 bp / stop −28 bp)
- **AND** a cycle decision SHALL NOT depend on whether a log record was written

### Requirement: The log file is a single file with a 200 MB ceiling and drops the oldest records

The diagnostic log SHALL be written to a **single** log file with a fixed size ceiling of **200 MB (209 715 200 bytes = 200 × 1024 × 1024)**. When the file reaches its ceiling and new records arrive, the oldest records SHALL be dropped **inside the same file** (tail truncation), so the file stays within its ceiling and the newest records are kept. A single record larger than the ceiling is never split: it is kept whole, so the file size SHALL stay ≤ `max(ceiling, largest single record)`. The truncation SHALL cut on a line boundary — the partial line at the start SHALL be discarded — so every record kept in the file remains readable. No backup file (`.1`, `.2`) SHALL be produced, `RotatingFileHandler`/`backupCount` SHALL NOT be used, and there SHALL be no time-based expiry: the file SHALL NOT grow without a ceiling and SHALL NOT rotate or expire records by age.

#### Scenario: Full file drops the oldest records

- **WHEN** the log file reaches its 200 MB ceiling and new records arrive
- **THEN** the oldest records SHALL be dropped so the file stays within the 200 MB ceiling
- **AND** the newest records SHALL be kept

#### Scenario: A record bigger than the ceiling stays whole

- **WHEN** a single record is larger than the ceiling
- **THEN** that record SHALL be kept whole instead of being split
- **AND** the file SHALL stay within `max(ceiling, largest single record)`

#### Scenario: Truncation preserves readable records at the line boundary

- **WHEN** the file is truncated because it reached its ceiling
- **THEN** the cut SHALL fall on a line boundary, discarding the partial leading line
- **AND** the first record of the truncated file SHALL remain readable

#### Scenario: No time-based rotation

- **WHEN** time passes without the file reaching its size ceiling
- **THEN** the file SHALL NOT rotate or expire records by age

### Requirement: Diagnostic logging ships DEV-only in this delivery

This delivery SHALL run the diagnostic logging only in the DEV environment (the DEV runtime-worker running the scalp loop). The production runtime-worker SHALL NOT gain the diagnostic logging in this delivery. Evidence for this delivery SHALL be a real log of several Jev calls — at least one success and one cycle refusal — observable in the DEV runtime-worker.

#### Scenario: DEV runtime-worker writes the records

- **WHEN** the DEV runtime-worker runs the scalp loop with a user's scalp ligado
- **THEN** the diagnostic log file SHALL collect entry/return records and refusal records in real runtime

#### Scenario: Production stays unchanged

- **WHEN** this delivery is deployed
- **THEN** the production runtime-worker SHALL NOT enable the diagnostic logging
- **AND** production behavior SHALL be unchanged

#### Scenario: Evidence includes a success and a refusal

- **WHEN** the delivery evidence is collected in DEV
- **THEN** the captured log SHALL contain at least one complete Jev call (entry and return) and at least one cycle refusal with its `skip_reason`

### Requirement: Diagnostic output is a log file only (no product surface)

The diagnostic output SHALL be a log file only: no new route, no landing page, no HTML, no Monitor or dashboard change, no new database, no export or Drive integration, and no navigable history of trades or cycles. The last refusal reason SHALL live in the log, not in the Monitor panel.

#### Scenario: No screen or route is added

- **WHEN** this change is applied
- **THEN** no UI, route, landing, HTML or panel change SHALL be introduced
- **AND** no authenticated route (`/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, landing) SHALL be borrowed or modified for this diagnostic
