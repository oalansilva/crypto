## ADDED Requirements

### Requirement: dsh child agentCtx sanitizes reasoning effort outside installModelSelection
The dsh Guard plugin SHALL attach reasoning-effort sanitization on each agent's own `agent.ctx`, including isolated children, so the child's model request MUST NOT send a refused effort (`none` / off / missing field that the openai-responses adapter turns into `"none"`). Attachment SHALL happen from `agent/created` with `{ global: true }` by calling a helper `attachAgentEffortGuards(agentCtx)` in `scripts/process-fsm/dsh_plugin_lib.js`. That helper MUST NOT throw (`agent/created` synchronous throw vetoes child publication). The `agent/request` listener on that `agentCtx` SHALL run `sanitizeReasoningEffort(await next())` and SHALL register with `{ prepend: true }` so it is outer to runtime `installModelSelection` even though it is installed after setup. The same attach SHALL register `agent/request-error` with `{ prepend: true }`. The sanitizer SHALL apply on **every** child `agent/request` of a continuable run (not only the first step). A host-only `ctx.on("agent/request")` from `apply(ctx)` with `inject=["systemPrompt","skills"]` SHALL NOT be the acceptance path: goldens MUST include a child event bus that does not inherit the host listeners, on which the #817 same-ctx waterfall stays insufficient. Rejected tokens and the `high` default remain those of `sanitizeReasoningEffort`. `guard.py` `decide()` MUST NOT gain this logic. `@deepseek-ai/dsh*` / `pi-ai` MUST NOT be vendored. `~/.dsh/settings.yaml` MUST NOT be the pin channel.

#### Scenario: Isolated child bus without attach keeps missing effort
- **WHEN** `apply(hostCtx)` registers the #817 host `agent/request` listener and a separate `childCtx` registers an `installModelSelection`-style strip after `next()`
- **AND** `agent/request` is dispatched only on `childCtx` (host hooks are not in that waterfall)
- **THEN** the returned config does not gain `reasoningEffort: "high"`
- **AND** this scenario MUST NOT pass by reusing the #817 same-ctx mock

#### Scenario: Prepend attach on child agentCtx wins over the strip
- **WHEN** `installModelSelection`-style strip is already registered on `childCtx`
- **AND** `apply(hostCtx)` then dispatches `agent/created` with `{ agent: { ctx: childCtx } }` so `attachAgentEffortGuards(childCtx)` runs with `{ prepend: true }`
- **AND** `agent/request` is dispatched on `childCtx` with a child descriptor of only provider and model
- **THEN** the returned config has `reasoningEffort` equal to `high`
- **AND** calling the helper without dispatching `agent/created` MUST NOT make this scenario pass

#### Scenario: Second continuable agent/request on the same child still has high
- **WHEN** `attachAgentEffortGuards` is installed on `childCtx`
- **AND** a second `agent/request` is dispatched on that same child after a parent `followup` / `send_message`
- **THEN** the returned config has `reasoningEffort` equal to `high`

#### Scenario: Attach without prepend after the strip loses
- **WHEN** the strip is already registered on `childCtx`
- **AND** sanitize-after-next is registered on the same `childCtx` without `{ prepend: true }`
- **THEN** the returned config does not have `reasoningEffort` equal to `high`

#### Scenario: Shared decide does not gain the child attach
- **WHEN** a reviewer inspects `scripts/process-fsm/guard.py` after this change
- **THEN** that source does not contain `reasoningEffort` or `dsh_reasoning_effort`
- **AND** `@deepseek-ai/dsh*` is not vendored

### Requirement: dsh child request-error retry is installed on the child agentCtx
The Guard SHALL register the existing one-shot `{ kind: "retry" }` this-class handler on the same `agent.ctx` as the sanitizer (`attachAgentEffortGuards`). `isReasoningEffortRejection` SHALL treat `Error.message`, `Error.code`, and `status` as facts even when those properties are non-enumerable. A this-class failure delivered as `new Error("...reasoning.effort does not support none...")` with `code` `INVALID_REQUEST` SHALL retry once on that child agent. A second this-class failure on the same agent SHALL call `next()`. Detection of child vs root remains the session header (`delegationDepth` / `origin` / `parentSession`), never `payload.provider`. The spawn gate `dsh_reasoning_effort_spawn` on the root SHALL still close after the first child this-class 400.

#### Scenario: Non-enumerable Error on the child agentCtx retries once
- **WHEN** `attachAgentEffortGuards` is installed on `childCtx`
- **AND** `agent/request-error` is dispatched on `childCtx` with `failure` an `Error` whose `message` contains `"reasoning.effort" does not support "none"` and `code` `INVALID_REQUEST`
- **THEN** the listener returns `{ kind: "retry" }`
- **AND** `next()` is not called
- **AND** a host-only `agent/request-error` listener that is not on `childCtx` MUST NOT make this scenario pass

#### Scenario: Second this-class Error on the same child is terminal
- **WHEN** the same child agent receives a second `agent/request-error` of this class on `childCtx`
- **THEN** `next()` is called
- **AND** the listener does not return `{ kind: "retry" }`

### Requirement: dsh parent sees stopReason and Diagnostic on the live settlement seam
When an isolated child's run ends in `turn/end` `reason.kind=error`, the parent-visible failure SHALL include `stopReason` and a `Diagnostic` taken from the provider text already recorded on that `turn/end` (witness: `INVALID_REQUEST` / `"reasoning.effort" does not support "none"`). The live vehicle for continuable start and for `send_message` is **not** a `tools/execute` throw: those `execute` calls succeed (`started subagent <id>` / message queued) and the 400 arrives later as runtime `notifySettlement` (`followup` if parent idle, `steer` if busy, `inject` only if the parent lineage is already closing) with `source.kind="subagent-settled"` and headline `Background subagent … failed before it finished` / `It left no closing message.` `Agent.inject()` SHALL NOT be the acceptance vehicle (it does not wake the parent and does not rewrite that notice). The plugin SHALL observe `session/event` with `{ global: true }` (presence-only still filters by carrier tag; a host listener without `global` SHALL NOT be the store) and store that `turn/end` by child session id. After the store records this-class `turn/end`, the plugin SHALL deliver `formatChildRunFailure` on the **same settlement vehicle** (`parent.followup` / `parent.steer`, resolved as `ctx.get("agents")?.get(header.parentSession)`). The plugin message `source` SHALL be `{ kind: "plugin", plugin: "covenant-flow-process-fsm-guard", form: "notice" }`. If `isReasoningEffortRejection` matches, the text SHALL name class `dsh_reasoning_effort_none` and SHALL say not to re-spawn the same preset (gate `dsh_reasoning_effort_spawn`). Formatter SHALL copy only the already-logged `reason.error.message` and MUST NOT `JSON.stringify(failure)`. Foreground one-shot MAY additionally inspect the `tools/execute` `next()` **result** (`isError` / `Error: subagent run failed`) and rewrite that content; a throw-only wrapper SHALL NOT satisfy this requirement. `send_message` SHALL be accepted on the settlement path, not by rewriting its successful `execute`. The plugin MUST NOT vendor `toStopReason` / `readResult` / `notifySettlement`. Unrelated 401 / rate-limit / Guard deny MUST NOT be labelled `dsh_reasoning_effort_none`.

#### Scenario: Foreground isError result is rewritten with Diagnostic
- **WHEN** a child `turn/end` stores this-class `INVALID_REQUEST` text
- **AND** parent `tools/execute` for one-shot `subagent` `next()` succeeds with `{ isError: true, content: "Error: subagent run failed" }`
- **THEN** the result content reaching the parent contains `stopReason` and `Diagnostic:` plus the provider message
- **AND** it contains `dsh_reasoning_effort_none`
- **AND** a wrapper that only catches a thrown `Error: subagent run failed` MUST fail this scenario

#### Scenario: Continuable start succeeds then settlement carries Diagnostic
- **WHEN** continuable `subagent` `tools/execute` `next()` succeeds with `started subagent <id>`
- **AND** `session/event` `{ global: true }` then records the child's `turn/end` 400 `INVALID_REQUEST`
- **THEN** the parent receives a `followup` or `steer` message containing `stopReason` and `Diagnostic:` plus `dsh_reasoning_effort_none`
- **AND** the generic `subagent-settled` headline `failed before it finished` / `It left no closing message.` alone MUST fail this scenario
- **AND** a host `session/event` listener without `{ global: true }` MUST NOT make this scenario pass
- **AND** `Agent.inject()` as the only delivery MUST NOT make this scenario pass

#### Scenario: send_message execute succeeds then settlement names the class
- **WHEN** a continuable child is already running
- **AND** the parent `send_message` `execute` succeeds (`message queued` / `{ messageId }`)
- **AND** the child's next turn ends in this-class `turn/end` 400
- **THEN** the parent-visible failure is the settlement path (`followup`/`steer` after that `turn/end`) containing `stopReason` and `Diagnostic`
- **AND** it names `dsh_reasoning_effort_none`
- **AND** rewriting a `send_message` throw of `subagent run failed` MUST NOT make this scenario pass

#### Scenario: Unrelated failures stay unlabelled as this class
- **WHEN** `formatChildRunFailure` or `isReasoningEffortRejection` receives a 401, a rate-limit, or a Guard deny without reasoning-effort needles
- **THEN** the class token `dsh_reasoning_effort_none` is absent
