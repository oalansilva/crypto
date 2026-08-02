## MODIFIED Requirements

### Requirement: Code Review MUST use an independent Luna thread after activation
After the project-scoped profiles are versioned and loaded, Code Review MUST run in a new Luna Max thread spawned with `fork_turns="none"`, distinct from the implementation thread. The reviewer MUST remain read-only by contract, MUST receive the exact diff, and MUST NOT implement its own fixes. When the runtime broadens the effective sandbox, the orchestrator MUST prove that no mutation was observed inside the mandatory before/after inventory and MUST disclose technically unobservable surfaces as residual risk. The bootstrap change that installs these profiles uses the explicit static-acceptance exception below.

#### Scenario: Post-activation implementation becomes reviewable
- **WHEN** a task started after profile activation has an implementation diff and focused evidence ready
- **THEN** the workflow spawns the exact Luna Max reviewer with `fork_turns="none"`, no implementation conversation history, and a self-contained review packet

#### Scenario: Reviewer receives a broadened effective sandbox
- **WHEN** the exact Luna reviewer reports an observable sandbox broader than read-only
- **THEN** Code Review MAY proceed only under the mandatory behavioral read-only contract, unchanged mandatory inventory and explicit residual-risk disclosure for unobservable surfaces

#### Scenario: Reviewer mutates state
- **WHEN** before/after evidence detects any mutation caused during review
- **THEN** the review is rejected, Code Review remains blocked, and the reviewer MUST NOT implement or repair the mutation

### Requirement: Model routing MUST fail closed
Every routed stage MUST require the exact configured agent name, model, reasoning effort, `fork_turns="none"`, and observable runtime security metadata. The orchestrator MUST prove `fork_turns="none"` from the explicit spawn request/result because the allowlisted runtime inspector does not expose that control. Missing, stale, conflicting, unavailable, or unobservable routing evidence MUST block the stage without fallback. A sandbox broader than the role's behavioral scope MUST be recorded as residual risk and MUST activate behavioral-containment evidence, but MUST NOT block the lane solely because it is broader.

#### Scenario: Expected profile is unavailable
- **WHEN** the client does not expose the exact profile required for the stage
- **THEN** the workflow stops that stage and reports the configuration blocker

#### Scenario: Model or effort differs
- **WHEN** runtime evidence differs from the profile's required model or reasoning effort
- **THEN** the workflow rejects the lane and MUST NOT substitute Terra, a built-in agent, or another effort

#### Scenario: Public runtime metadata is incomplete
- **WHEN** spawn details omit agent type, model, effort, sandbox policy type, or permission profile type
- **THEN** the workflow uses the exact-thread local allowlisted inspector and blocks if required values remain missing, ambiguous, or conflicting

#### Scenario: Sandbox is broader than the requested behavioral scope
- **WHEN** agent type, model, effort and thread isolation match but the observable runtime sandbox is broadened
- **THEN** the workflow applies behavioral containment, records the residual risk and decides the lane from scope and before/after evidence rather than sandbox equality

## ADDED Requirements

### Requirement: Every Luna lane MUST use behaviorally verified containment
The orchestrator MUST apply behavioral containment to every Luna lane regardless of the effective sandbox. Before spawning, it MUST record the bounded state relevant to the lane and assign exact ownership, allowed actions, prohibited actions and external-system limits. After return, it MUST independently inspect the mandatory inventory, MUST reject every observed out-of-scope mutation, unauthorized auditable external action, difference or undeclared exclusion, and MUST classify technically unobservable surfaces as residual risk rather than claim zero global mutation.

#### Scenario: Implementer respects assigned ownership
- **WHEN** a Luna implementer returns work
- **THEN** the orchestrator verifies that only assigned paths changed and that no prohibited commit, push, PR, board, service or external action occurred

#### Scenario: Reviewer returns findings
- **WHEN** a Luna reviewer returns its review
- **THEN** the orchestrator verifies that every named repository/worktree mandatory inventory remained unchanged and records unobservable surfaces as residual risk before accepting the findings

#### Scenario: Release manager acts on an authorized package
- **WHEN** a Luna release manager returns from an explicitly authorized release
- **THEN** the orchestrator verifies that actions and mutations remained within the homologated package and the authorized release checklist

#### Scenario: Behavioral evidence is incomplete
- **WHEN** the orchestrator cannot compare the relevant before/after state or cannot classify an observed mutation
- **THEN** the stage remains blocked and MUST NOT be reported complete

### Requirement: Option 2 MUST remain the standard without weakening host security
The Luna workflow MUST use behavioral containment as its standard operating contract and MUST NOT require disabling or modifying host security controls to obtain a narrower sandbox.

#### Scenario: Narrow sandbox cannot initialize under host policy
- **WHEN** bubblewrap, AppArmor, user namespaces or another preserved host control prevents a narrow sandbox from starting
- **THEN** the workflow keeps the host protection unchanged and uses the behaviorally contained lane with explicit residual-risk evidence

#### Scenario: Runtime supplies a narrower sandbox
- **WHEN** a future runtime supplies a sandbox narrower than danger-full-access
- **THEN** the workflow accepts the additional protection but still performs all behavioral-containment checks
