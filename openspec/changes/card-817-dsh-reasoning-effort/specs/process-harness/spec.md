## ADDED Requirements

### Requirement: dsh plugin sanitizes rejected reasoning effort on every model request
The dsh Guard plugin SHALL sanitize reasoning effort in Cordis `agent/request` so the model call MUST NOT send a value this session's chat model rejects (witness: `"none"` / effort off). The sanitizer SHALL live as `sanitizeReasoningEffort` in `scripts/process-fsm/dsh_plugin_lib.js` and SHALL be called from `.dsh/plugin/process-fsm-guard.js` as `ctx.on("agent/request", async (payload, next) => sanitizeReasoningEffort(await next()))`. Sanitizing MUST run after `await next()` so it wins over the runtime `installModelSelection` strip that clears inherited effort when a child descriptor has only `agentProvider`+`agentModel`. Rejected tokens (case-insensitive, trimmed) are `none`, `off`, empty string, and JSON `null`. An already-accepted value in `{minimal, low, medium, high}` SHALL be kept. A missing field or a rejected token SHALL become `reasoningEffort: "high"` (the agent default and the turn-10 witness). Nested `reasoning.effort` SHALL be sanitized the same way and MUST NOT remain `none` beside `reasoningEffort`. The mapping SHALL apply to every provider/model in the dsh session (Q2=A); it MUST NOT be an allowlist of `muse-spark-*`. The mapping SHALL NOT live in `~/.dsh/settings.yaml` as the pin channel and SHALL NOT vendor `deepseek-ai/deepseek-harness`. `scripts/process-fsm/guard.py` `decide()` MUST NOT gain this logic. `inject` MAY stay `["systemPrompt", "skills"]`. Write-like deny, grill-shaped deny, and `isCordisRestricted` MUST still pass.

#### Scenario: Rejected none becomes high
- **WHEN** `sanitizeReasoningEffort` receives `reasoningEffort` equal to `none` or `off` (any case) or nested `reasoning.effort` equal to `none`
- **THEN** the returned config has `reasoningEffort` equal to `high`
- **AND** nested `none` is absent

#### Scenario: Accepted value is kept and missing becomes high
- **WHEN** `sanitizeReasoningEffort` receives `reasoningEffort` equal to `medium`
- **THEN** the returned config keeps `medium`
- **AND** a config with no effort field returns `reasoningEffort` equal to `high`

#### Scenario: Sanitize wins over inherited-effort strip
- **WHEN** `apply(ctx)` registers `agent/request` and an inner waterfall listener strips `reasoningEffort` the way `installModelSelection` does
- **THEN** the config returned to the loop still has `reasoningEffort` equal to `high`
- **AND** a child descriptor that only has provider and model also returns `reasoningEffort` equal to `high`

#### Scenario: Shared decide does not gain the mapper
- **WHEN** a reviewer inspects `scripts/process-fsm/guard.py` after this change
- **THEN** that source does not contain `reasoningEffort` or `dsh_reasoning_effort`
- **AND** `deepseek-ai/deepseek-harness` is not vendored

### Requirement: dsh recovers the root turn on this-class 400 and stops same-preset child spawns after the first child rejection
The plugin SHALL classify this-class rejection with `isReasoningEffortRejection(failure)`: the normalized failure facts contain a reasoning-effort needle (`reasoning.effort` or `reasoningEffort` or `UNSUPPORTED_REASONING_EFFORT`) together with a rejected-token needle (`none` or `off` or `does not support`) or an `INVALID_REQUEST` / `400` together with those needles. Rate-limit, `401`, and Guard deny MUST NOT match. On Cordis `agent/request-error` the payload is `{ agent, turn, step, provider, failure, retryPolicy, signal }`. `payload.provider` is the **LLM provider** (incident witness `opencodealan`) and MUST NOT be used to tell child from root. The **same** agent (session id on `payload.agent`, not `payload.turn` alone) MAY retry once (`{ kind: "retry" }` without `next()`); a second this-class failure on that agent MUST call `next()`. That retry is a model-request recovery, not a new `subagent` spawn and not the #518 empty-spawn retry. A child SHALL be detected **only** from `payload.agent.session.header`: `delegationDepth >= 1` **or** `origin === "subagent"` **or** `parentSession` present. Apply MUST read that header and MUST NOT import `@deepseek-ai/dsh-subagent`. After the first this-class 400 on a child, the plugin SHALL add `header.parentSession` (fallback: caller/root session id) to an in-memory `Set`. Root `tools/pre-execute` SHALL consult that `Set` (the root session is a member) and deny further `subagent` and `subagent_fork` with reason containing `dsh_reasoning_effort_spawn` without `next()`. The gate key MUST NOT be `payload.turn`: that field is the failing agent's turn (isolated child starts at `1`; the incident root was `9`) and is not visible to the other agent's `tools/pre-execute`. A this-class 400 on the **root** (`delegationDepth` 0, no `origin: "subagent"`, no `parentSession`) MUST NOT close that spawn gate (the recovered root MAY spawn the happy-path Apply/reviewer). Listener order in `tools/pre-execute` SHALL be: grill-shaped deny, then this spawn gate, then `isCordisRestricted`, then `runGuard`. The root SHALL record `ERROR: subagent spawn failed/empty` and MAY complete the step itself with an explicit residual; silent fallback remains forbidden. Pytest goldens for the waterfall MUST `import { apply }` from `.dsh/plugin/process-fsm-guard.js`. Golden E7 MUST fire `agent/request-error` on a child with `turn: 1`, `provider: "opencodealan"`, `header.delegationDepth: 1`, `origin: "subagent"`, and a `parentSession`, then `tools/pre-execute` on the **root** with a **different** `turn` (witness `9`) for Apply and reviewer `subagent` calls; it MUST NOT pass with `provider: "spawn"` or with equal turns on both sides.

#### Scenario: Root first this-class 400 retries the same request
- **WHEN** `apply(ctx)` then `agent/request-error` runs for a root agent (`header.delegationDepth` 0, no `parentSession`) with `provider` `opencodealan` and this-class failure for the first time on that agent
- **THEN** the listener returns `{ kind: "retry" }`
- **AND** `next()` is not called

#### Scenario: Second this-class failure on the same agent is terminal
- **WHEN** the same agent (same session id) receives a second `agent/request-error` of this class
- **THEN** `next()` is called
- **AND** the listener does not return `{ kind: "retry" }`

#### Scenario: First child this-class 400 blocks further subagent on the root
- **WHEN** `agent/request-error` runs for a child with `turn` 1, `provider` `opencodealan`, `header.delegationDepth` 1, `origin` `subagent`, and `parentSession` equal to the root session
- **AND** `tools/pre-execute` then runs on the **root** agent with a different `turn` (witness 9) for `subagent` Apply or `subagent` reviewer
- **THEN** both calls return `{ kind: "deny" }` with reason `dsh_reasoning_effort_spawn`
- **AND** `next()` is not called
- **AND** a mock that keys the gate on `payload.turn` or that treats `provider === "spawn"` as the child test MUST fail this scenario

#### Scenario: Root this-class 400 does not close the spawn gate
- **WHEN** `agent/request-error` classifies this class on the root only (`delegationDepth` 0, `provider` `opencodealan`, no `parentSession`)
- **AND** `tools/pre-execute` runs for `subagent` whose description and prompt do not contain `grill-card`
- **THEN** `next()` is called
- **AND** grill-shaped `subagent` is still denied by `dsh_grill_spawn`

#### Scenario: Unrelated failures are not this class
- **WHEN** `isReasoningEffortRejection` receives a 401, a rate-limit, or a Guard deny without reasoning-effort needles
- **THEN** it returns false
