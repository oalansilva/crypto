## ADDED Requirements

### Requirement: dsh this-class reasoning-effort 400 MUST NOT consume the empty-spawn retry
On the dsh client, after the first this-class reasoning-effort rejection (400 / `INVALID_REQUEST` sending effort off / `none`) on an isolated Apply or reviewer **child** in the turn, the runtime root MUST NOT spawn another `subagent` / `subagent_fork` with the same preset, including the one-retry empty-spawn path from #518. The handoff SHALL record `ERROR: subagent spawn failed/empty` and the root MAY finish the step with an explicit residual. Silent fallback remains forbidden. Happy path remains: each isolated Apply and each of `diff-reviewer` and `code-reviewer` enters `turn/start`, runs at least one tool, and leaves a closing message, with zero this-class rejections on that spawn. Cursor and Grok keep the existing one-retry empty-spawn rule unchanged. This requirement MUST NOT reopen #518 / #569 as work, MUST NOT deny every `subagent`, and MUST NOT change `process-fsm.yaml`.

#### Scenario: First dead dsh reviewer does not birth the pair via retry
- **WHEN** the dsh root's first isolated Apply or reviewer child in the turn dies from this-class reasoning-effort 400
- **THEN** the root MUST NOT spawn a retry of that child or the other reviewer with the same preset
- **AND** the handoff records `ERROR: subagent spawn failed/empty`
- **AND** the root MAY complete the review itself only after that explicit residual

#### Scenario: Cursor empty-spawn retry is unchanged
- **WHEN** the client is Cursor or Grok and a reviewer Task returns 0 messages or 0 parts without this-class reasoning-effort 400
- **THEN** the existing one-retry empty-spawn rule still applies
- **AND** this requirement does not alter that path
