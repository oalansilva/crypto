## ADDED Requirements

### Requirement: Agents MUST use bounded native CI waiting
Agent instructions MUST require one owner and one native watcher for all reported pending pull-request checks, with an explicit timeout and no hand-written polling loop. The watcher MUST NOT limit observation to branch-protection-required checks because every started check needs a terminal result.

#### Scenario: Required checks are still running
- **WHEN** an agent must wait for required pull-request checks
- **THEN** it uses a native unfiltered `gh pr checks --watch` command with bounded interval and timeout instead of a `for` or `while` loop with `sleep`

#### Scenario: Long wait supports background execution
- **WHEN** the expected CI wait exceeds 60 seconds and the client supports background tasks
- **THEN** the watcher runs in the background while the agent performs independent in-scope work

### Requirement: CI waiting MUST fail closed before merge
Agent instructions MUST stop the merge phase when the watcher times out, any reported check fails, or mergeability remains blocked. A manual merge attempt MUST occur only after successful terminal checks and one final mergeability query. Each observed clean state permits at most one attempt; a failed attempt requires diagnosis and a fresh complete readiness check before retry.

#### Scenario: Watcher fails or times out
- **WHEN** the native watcher returns failure or reaches its timeout
- **THEN** the agent records the blocking state and does not invoke merge

#### Scenario: Checks succeed and pull request is clean
- **WHEN** all required checks succeed and one final query reports the pull request clean and mergeable
- **THEN** the agent performs at most one authorized manual merge attempt for that observed state
