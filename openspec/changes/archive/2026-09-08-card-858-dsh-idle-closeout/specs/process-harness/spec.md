## ADDED Requirements

### Requirement: dsh session stays occupied while the next step is still the agent's
On dsh, while the next step is still the agent's (wait for a check, isolated child returning, integrate after green), the session SHALL remain occupied until that step decides. The GUI MUST NOT go idle waiting for a human `continue`. Occupied means the current turn stays open: `job_output` with `wait: true` MUST not return to the model while the job is still `running` unless a total wait ceiling of 45 minutes has elapsed, and `agent/turn-stopping` with `{ global: true }` MUST `steer` when the owner still has jobs in `running`/`stopping` or a live isolated child. `maxConsecutiveWakes` (host default 3) SHALL remain a safety net and MUST NOT be raised as the acceptance path. `Agent.inject()` SHALL NOT be the vehicle that keeps the session occupied. `guard.py` `decide()` MUST NOT gain needles for this rule. `@deepseek-ai/dsh*` MUST NOT be vendored. Auto MUST remain off. Human gates (priorizar, aprovar design, homologar) MUST still be allowed to idle when no agent-owned job or child is pending.

#### Scenario: job_output wait does not return while the check is still running
- **WHEN** the Guard `apply` wraps `job_output` with `wait: true` and the job snapshot remains `running` after one host wait
- **THEN** that `tools/execute` does not return to the model until the job is terminal or 45 minutes total have elapsed
- **AND** a single host wait of 30 seconds or 10 minutes that returns `[status: running]` MUST fail this scenario
- **AND** pytest goldens MUST `import { apply }` from `.dsh/plugin/process-fsm-guard.js`

#### Scenario: turn-stopping steers when agent work is still pending
- **WHEN** `agent/turn-stopping` `{ global: true }` fires and the owner has a running/stopping job or a live isolated child
- **THEN** the plugin calls `steer` on that agent with a plugin notice (`source.kind="plugin"`, `form="notice"`)
- **AND** a host listener without `{ global: true }` MUST NOT make this scenario pass
- **AND** `inject()` as the only delivery MUST NOT make this scenario pass

#### Scenario: turn-stopping does not steal human gates
- **WHEN** `agent/turn-stopping` fires and the owner has no running/stopping job and no live isolated child
- **THEN** the plugin does not `steer`
- **AND** the session MAY go idle (Aprovação de Design / Em Refinamento waiting for Alan)

#### Scenario: wait without timeout_ms is rewritten to the aligned cap
- **WHEN** `tools/pre-execute` sees `job_output` with `wait: true` and no `timeout_ms`
- **THEN** arguments reaching execute include `timeout_ms` equal to 2400000 (40 minutes)
- **AND** leaving the host default 30000 MUST fail this scenario

### Requirement: dsh tool-jobs patch aligns the wait cap and does not raise wake budget
`.dsh/cordis.patch.yml` SHALL overlay the existing host row `id: tool-jobs` with `config.maxWaitTimeoutMs: 2400000`. The overlay MUST NOT set `maxConsecutiveWakes` above the host default 3. `completionDelivery` MUST remain the host default `wakeup`. Dual-write of T0–T17 into `.dsh/` remains forbidden. `dsh plugin add` remains not the pin channel.

#### Scenario: patch raises wait cap only
- **WHEN** a reviewer reads `.dsh/cordis.patch.yml` after this change
- **THEN** it contains a non-insert patch targeting `id: tool-jobs` with `maxWaitTimeoutMs` 2400000
- **AND** it does not raise `maxConsecutiveWakes`
- **AND** it does not contain a T0–T17 table

### Requirement: dsh dead provider turn retries once then fails visibly
The dsh Guard SHALL treat a dead provider turn as class `dsh_dead_turn`: empty response (`EMPTY_RESPONSE` or zero content), usage-limit/quota wording, or missing session at the provider (`SESSION_NOT_FOUND` / session missing). On `agent/request-error` (host and child `agent.ctx`), the first this-class failure for an agent SHALL return `{ kind: "retry" }`. A second this-class failure on the same agent SHALL call `next()` and the blockage MUST be visible (not silence). The handler MUST NOT loop. The retry set MUST be distinct from `dsh_reasoning_effort_none`. `guard.py` `decide()` MUST NOT gain this classifier.

#### Scenario: first empty response retries once
- **WHEN** `agent/request-error` is dispatched with an `EMPTY_RESPONSE` (or empty-content) failure
- **AND** that agent has not yet retried `dsh_dead_turn`
- **THEN** the listener returns `{ kind: "retry" }`
- **AND** `next()` is not called

#### Scenario: second dead-turn failure is visible and not retried
- **WHEN** the same agent receives a second `dsh_dead_turn` `agent/request-error`
- **THEN** `next()` is called
- **AND** the listener does not return `{ kind: "retry" }`
- **AND** a third automatic retry MUST NOT occur
