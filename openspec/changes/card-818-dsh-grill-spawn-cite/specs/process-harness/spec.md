## MODIFIED Requirements

### Requirement: dsh Guard denies grill-shaped subagent spawn
The grill-shaped deny SHALL exist **only** as `isGrillShapedSpawn` in `scripts/process-fsm/dsh_plugin_lib.js`, called from `.dsh/plugin/process-fsm-guard.js` in Cordis `tools/pre-execute` **before** `runGuard` / `decide()`. `scripts/process-fsm/guard.py` MUST remain unchanged: its source MUST NOT contain `grill-card`, `dsh_grill_spawn`, or `isGrillShapedSpawn`. The plugin SHALL deny tool names `subagent` and `subagent_fork` when the spawn is **papel de grelha**, not when it is **citação** of a closed grill ritual. Matching SHALL use `String.includes` after `toLowerCase()` (not a regex) and MUST NOT live in `decide()`. Papel: `arguments.description` contains the substring `grill-card`, **or** `arguments.prompt` (or a parse-fail raw arguments string treated as prompt) contains `grill-card` **and** contains none of the pinned citation markers `fronteira vazia`, `do not re-interview`, `não reentrevistar`, `do not invoke grill-card`, `não invocar grill-card`, `closed grill`, `grill-card dod`, `dod grelhado`, `grilled dod`. Citação: description does not contain `grill-card` **and** prompt contains `grill-card` **and** at least one pinned citation marker — this deny MUST NOT fire (`next()` SHALL run). If `arguments` is a JSON string, the plugin SHALL parse it and apply the same fields; parse failure SHALL scan the raw string as prompt. Nested copies SHALL be collected only from `description` and `prompt` keys at any depth (recurse into object values). The helper MUST NOT treat `JSON.stringify` of the whole arguments object as a haystack. A matching papel call MUST return `{ kind: "deny", reason }` containing `dsh_grill_spawn` and MUST NOT call `next()`. `run_in_background` MUST NOT affect the match. Unrelated `subagent` / `subagent_fork` (no needle in description/prompt) MUST call `next()` (fail-open). Tools that are not `subagent` or `subagent_fork` MUST NOT be denied by this heuristic (including Cursor `Task`, Grok `spawn_subagent`, and OpenCode `task` if they appear). Pytest goldens G1–G9 MUST `import { apply }` from `.dsh/plugin/process-fsm-guard.js` and invoke `tools/pre-execute` (same pattern as existing dsh adapter goldens); they MUST NOT pass solely by unit-testing a Python helper inside `decide()`. G12 (Design-author citation allow) MUST use the same `apply` + `pre-execute` path. This deny SHALL be **in addition to** write-like deny and `isCordisRestricted`. `isCordisRestricted` MUST remain `cordis_*` only. The heuristic MUST NOT be a Cursor `preToolUse` matcher and MUST NOT be a Grok hook. The `tools/pre-execute` listener MUST remain registered before `ctx.skills.registerProvider`; a throw from the provider MUST NOT skip deny. Write-deny goldens of the dsh adapter MUST still pass. OpenCode `runGuard` on every `tool.execute.before` remains out of scope for this Task-shaped deny. Grill deny SHALL remain **first** among spawn denys: `isGrillShapedSpawn` before `runGuard`, reason `dsh_grill_spawn`, without `next()` on match. That order is the meaning of «listener unchanged» — the plugin file MUST NOT be required byte-identical to pin `v1.1.6`. Sibling #817 MAY insert `dsh_reasoning_effort_spawn` after grill and before cordis, and MAY add `agent/request` / `agent/request-error`; this change MUST NOT revert those. This requirement MUST NOT reopen #786 (dsh root grills; grill **papel** stays deny; matcher stays out of `guard.py`) and MUST NOT reopen #790.

#### Scenario: G1-G9 go through plugin apply
- **WHEN** pytest goldens G1–G9 run
- **THEN** they `import { apply }` from `.dsh/plugin/process-fsm-guard.js` and call `tools/pre-execute`
- **AND** they MUST NOT pass solely by unit-testing a Python helper inside `decide()`

#### Scenario: grill-card description on subagent is denied
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` with `arguments.description` equal to `grill-card 701`
- **THEN** the listener returns `{ kind: "deny" }` with reason `dsh_grill_spawn`
- **AND** `next()` is not called
- **AND** the deny is returned before `runGuard`

#### Scenario: needle in prompt or mixed case still denies
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent_fork` and only `arguments.prompt` contains `Grill-Card` (ROLE; no pinned citation marker)
- **THEN** the call is denied
- **AND** the same deny holds if `run_in_background` is `false`

#### Scenario: unrelated subagent is fail-open
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` whose description and prompt do not contain `grill-card`
- **THEN** `next()` is called
- **AND** the grill heuristic does not deny

#### Scenario: Cursor-shaped and OpenCode task tools call next
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `Task`, `spawn_subagent`, or OpenCode `task` with `prompt` containing `grill-card`
- **THEN** `next()` is called for each of those tool names
- **AND** the result is not `{ kind: "deny" }` whose reason contains `dsh_grill_spawn`

#### Scenario: write deny still works if registerProvider throws
- **WHEN** `apply(ctx)` throws from `registerProvider` and a later `tools/pre-execute` is an illegal product `edit` or a grill-shaped `subagent`
- **THEN** `apply` itself does not throw
- **AND** both calls return `{ kind: "deny" }`
- **AND** `next()` is not called

#### Scenario: shared decide() does not gain the spawn rule
- **WHEN** a reviewer inspects `scripts/process-fsm/guard.py` and `.cursor/hooks.json` after this change
- **THEN** the source of `guard.py` does not contain `grill-card`, `dsh_grill_spawn`, or `isGrillShapedSpawn`
- **AND** Cursor `preToolUse` matcher is still `Write|StrReplace|Delete|EditNotebook`
- **AND** `isCordisRestricted` still matches only `cordis_*` names

#### Scenario: decide() allows Task with grill-card prompt
- **WHEN** Python `decide()` receives a no-path payload with `tool`/`tool_name` `Task` and `args.prompt` containing `grill-card`
- **THEN** it returns `permission: allow`
- **AND** it MUST NOT invent a new FSM event for this payload

#### Scenario: Design-author citation of closed grill ritual is not this deny
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` with `arguments.description` equal to `design-autor 818` (no `grill-card` in description) and `arguments.prompt` containing `grill-card fronteira vazia`
- **THEN** `next()` is called
- **AND** the result is not `{ kind: "deny" }` whose reason contains `dsh_grill_spawn`

#### Scenario: isolated Apply and reviewer citation is not this deny
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` whose description is `apply 818` or `diff-reviewer 818` and whose prompt cites the grilled DoD (`grill-card dod`, `dod grelhado`, or `closed grill` together with `grill-card`)
- **THEN** `next()` is called
- **AND** the result is not `{ kind: "deny" }` whose reason contains `dsh_grill_spawn`

#### Scenario: nested citation outside description and prompt is not this deny
- **WHEN** `apply(ctx)` then `tools/pre-execute` runs for `subagent` with description `design-autor 818` and a nested non-`description`/non-`prompt` field containing `grill-card`
- **THEN** `next()` is called
- **AND** `isGrillShapedSpawn` is false for that payload
- **AND** a nested `inner.prompt` value `x grill-card y` without a citation marker still makes `isGrillShapedSpawn` true

#### Scenario: grill spawn deny stays first and does not revert sibling #817
- **WHEN** Apply lands this change on a product tip that already has #817 (`dsh_reasoning_effort_spawn` between grill and cordis, plus `agent/request`)
- **THEN** `isGrillShapedSpawn` still runs before `runGuard` and still returns reason `dsh_grill_spawn` without `next()` on papel
- **AND** the #817 gate and `agent/request` listeners remain
- **AND** `.dsh/plugin/process-fsm-guard.js` is not required to match pin `v1.1.6` byte-for-byte
